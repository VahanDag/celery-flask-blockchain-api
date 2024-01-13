from google.cloud import secretmanager

# Google Cloud projesinin ID'si
project_id = "flutter-app-demo-da31e"
# Çekmek istediğiniz secret'ın adı
secret_id = "address-test"

# Secret Manager istemcisini başlat
client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

# Secret versiyonunu çek
response = client.access_secret_version(request={"name": name})

# Secret'ın değerini al
secret_value = response.payload.data.decode("UTF-8")
print("Secret Value:", secret_value)
