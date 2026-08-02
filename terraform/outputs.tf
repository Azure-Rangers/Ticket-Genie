# --- Web App Outputs ---

output "webapp_url" {
  value       = "https://${azurerm_linux_web_app.app.default_hostname}"
  description = "The public URL of the deployed Linux Web App"
}

output "webapp_name" {
  value       = azurerm_linux_web_app.app.name
  description = "The name of the Azure Web App resource"
}

# --- Database Outputs ---

output "sql_server_fqdn" {
  value       = azurerm_mssql_server.sql.fully_qualified_domain_name
  description = "Fully qualified domain name of the Azure SQL Server"
}

output "database_name" {
  value       = azurerm_mssql_database.db.name
  description = "Name of the Azure SQL Database"
}

# --- Key Vault Outputs ---

output "key_vault_name" {
  value       = azurerm_key_vault.kv.name
  description = "Name of the Key Vault storing secrets"
}

output "key_vault_secret_name" {
  value       = azurerm_key_vault_secret.db_password.name
  description = "Key Vault secret name holding the SQL admin password"
}