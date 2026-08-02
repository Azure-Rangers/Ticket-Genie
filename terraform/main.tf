terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "Azure_Rangers"
    storage_account_name = "sttfstate12345"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
    use_oidc             = true
  }
}

provider "azurerm" {
  features {}
  use_oidc = true
}

# --- Reference Existing Resource Group ---

data "azurerm_resource_group" "rg" {
  name = "Azure_Rangers"
}

# --- Generate Random Password ---

resource "random_password" "db_password" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# --- Azure SQL Database ---

resource "azurerm_mssql_server" "sql" {
  name                         = "sql-server-app-prod"
  resource_group_name          = data.azurerm_resource_group.rg.name
  location                     = data.azurerm_resource_group.rg.location
  version                      = "12.0"
  administrator_login          = "dbadmin"
  administrator_login_password = random_password.db_password.result
}

resource "azurerm_mssql_database" "db" {
  name        = "app-db"
  server_id   = azurerm_mssql_server.sql.id
  collation   = "SQL_Latin1_General_CP1_CI_AS"
  sku_name    = "Basic"
  max_size_gb = 2
}

resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.sql.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# --- Web App ---

resource "azurerm_service_plan" "asp" {
  name                = "asp-app-prod"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "app" {
  name                = "webapp-prod-12345"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = azurerm_service_plan.asp.location
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    always_on = true
    application_stack {
      node_version = "18-lts"
    }
  }

  app_settings = {
    "DATABASE_URL" = "Server=tcp:${azurerm_mssql_server.sql.fully_qualified_domain_name},1433;Initial Catalog=${azurerm_mssql_database.db.name};Persist Security Info=False;User ID=${azurerm_mssql_server.sql.administrator_login};Password=${random_password.db_password.result};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
  }
}
 
 