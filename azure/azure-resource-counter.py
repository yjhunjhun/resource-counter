import logging
import csv
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from tqdm import tqdm
import threading

# Configure logging
logging.basicConfig(filename='azure_resource_counts.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

#Authenticate and return an Azure client credential.
def authenticate_client(client_id, client_secret, tenant_id):
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    return credential

#List Azure subscriptions using the provided credential
def list_subscriptions(credential):
    subscription_client = SubscriptionClient(credential)
    return list(subscription_client.subscriptions.list())

def count_virtual_machines(credential, subscription_id, resource_group):
    compute_client = ComputeManagementClient(credential, subscription_id)
    total_vm_count = 0

    try:
        vm_paged = compute_client.virtual_machines.list(resource_group)
        for _ in vm_paged:
            total_vm_count += 1

        return total_vm_count
    except Exception as e:
        logging.error(f"Error counting VMs in {resource_group}: {str(e)}")
        return 0

def count_web_apps(credential, subscription_id, resource_group):
    website_client = WebSiteManagementClient(credential, subscription_id)
    total_web_app_count = 0

    try:
        web_apps = website_client.web_apps.list_by_resource_group(resource_group)
        for _ in web_apps:
            total_web_app_count += 1

        return total_web_app_count
    except Exception as e:
        logging.error(f"Error counting Web Apps in {resource_group}: {str(e)}")
        return 0

def count_container_instances(credential, subscription_id, resource_group):
    container_instance_client = ContainerInstanceManagementClient(credential, subscription_id)
    total_aci_count = 0

    try:
        aci_paged = container_instance_client.container_groups.list_by_resource_group(resource_group)
        for _ in aci_paged:
            total_aci_count += 1

        return total_aci_count
    except Exception as e:
        logging.error(f"Error counting ACIs in {resource_group}: {str(e)}")
        return 0

def count_aks_clusters(credential, subscription_id, resource_group):
    container_service_client = ContainerServiceClient(credential, subscription_id)
    total_aks_count = 0

    try:
        aks_paged = container_service_client.managed_clusters.list_by_resource_group(resource_group)
        for _ in aks_paged:
            total_aks_count += 1

        return total_aks_count
    except Exception as e:
        logging.error(f"Error counting AKS clusters in {resource_group}: {str(e)}")
        return 0

def count_acr_repositories(credential, subscription_id, resource_group):
    container_registry_client = ContainerRegistryManagementClient(credential, subscription_id)
    total_acr_repo_count = 0

    try:
        acr_repos = container_registry_client.registries.list_by_resource_group(resource_group)
        for _ in acr_repos:
            total_acr_repo_count += 1

        return total_acr_repo_count
    except Exception as e:
        logging.error(f"Error counting ACR repositories in {resource_group}: {str(e)}")
        return 0

def count_acr_images(credential, subscription_id, resource_group):
    container_registry_client = ContainerRegistryManagementClient(credential, subscription_id)
    total_acr_image_count = 0

    try:
        acr_repos = container_registry_client.registries.list_by_resource_group(resource_group)
        for repo in acr_repos:
            repo_name = repo.name
            acr_client = container_registry_client.registries.get(resource_group, repo_name)
            acr_images = list(acr_client.list_manifests(repo_name))
            total_acr_image_count += len(acr_images)

        return total_acr_image_count
    except Exception as e:
        logging.error(f"Error counting ACR images in {resource_group}: {str(e)}")
        return 0

def count_azure_functions(credential, subscription_id, resource_group):
    web_client = WebSiteManagementClient(credential, subscription_id)
    total_azure_functions = 0

    try:
        function_apps = web_client.app_service_plans.list_by_resource_group(resource_group)
        for app_service_plan in function_apps:
            if "FunctionApp" in app_service_plan.name:
                function_apps = web_client.web_apps.list_by_resource_group(resource_group)
                total_azure_functions += sum(1 for _ in function_apps)

        return total_azure_functions
    except Exception as e:
        logging.error(f"Error counting Azure Functions in {resource_group}: {str(e)}")
        return 0

def count_resources_in_resource_group(credential, subscription_id, resource_group, result_dict):
    result_dict[resource_group] = {
        "Virtual Machines": count_virtual_machines(credential, subscription_id, resource_group),
        "Web Apps": count_web_apps(credential, subscription_id, resource_group),
        "Container Instances": count_container_instances(credential, subscription_id, resource_group),
        "AKS Clusters": count_aks_clusters(credential, subscription_id, resource_group),
        "ACR Repositories": count_acr_repositories(credential, subscription_id, resource_group),
        "ACR Images": count_acr_images(credential, subscription_id, resource_group),
        "Azure Functions": count_azure_functions(credential, subscription_id, resource_group),
    }

def process_subscription_with_progress_bar(credential, subscription, csv_writer):
    subscription_id = subscription.subscription_id
    logging.info(f"Subscription ID: {subscription_id}")

    resource_groups = ResourceManagementClient(credential, subscription_id).resource_groups.list()

    result_dict = {}
    threads = []

    # Create threads for counting resources in each resource group
    for resource_group in resource_groups:
        thread = threading.Thread(target=count_resources_in_resource_group, args=(credential, subscription_id, resource_group.name, result_dict))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Sum counts across resource groups
    total_counts = {
        "Virtual Machines": 0,
        "Web Apps": 0,
        "Container Instances": 0,
        "AKS Clusters": 0,
        "ACR Repositories": 0,
        "ACR Images": 0,
        "Azure Functions": 0,
    }

    for resource_group, counts in result_dict.items():
        for resource_type, count in counts.items():
            total_counts[resource_type] += count

    csv_writer.writerow([subscription_id] + list(total_counts.values()))
    logging.info(f"Counts for Subscription {subscription_id} saved in CSV")


def main():
    client_id = input("Enter Azure Client ID: ")
    client_secret = input("Enter Azure Client Secret: ")
    tenant_id = input("Enter Azure Tenant ID: ")

    credential = authenticate_client(client_id, client_secret, tenant_id)

    subscriptions = list_subscriptions(credential)
    logging.info(f"Total Subscriptions: {len(subscriptions)}")
    logging.info("-" * 50)

    # Prompt the user to select the subscription
    print("Select an option:")
    print("1. Process all subscriptions")
    print("2. Process a single subscription")
    option = input("Enter your choice (1/2): ")

    with open('azure_resource_counts.csv', mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Added headers for each resource type
        csv_writer.writerow(['Subscription ID', 'Virtual Machines', 'Web Apps', 'Container Instances', 'AKS Clusters',
                             'ACR Repositories', 'ACR Images', 'Azure Functions'])

        if option == "1":
            pbar = tqdm(subscriptions, desc="Processing Subscriptions", unit="subscription")
            for subscription in pbar:
                process_subscription_with_progress_bar(credential, subscription, csv_writer)
        elif option == "2":
            subscription_id = input("Enter the Subscription ID to process: ")
            subscription = next((sub for sub in subscriptions if sub.subscription_id == subscription_id), None)
            if subscription:
                process_subscription_with_progress_bar(credential, subscription, csv_writer)
            else:
                print("Subscription not found.")
        else:
            print("Invalid option. Please select 1 or 2.")


if __name__ == "__main__":
    main()
