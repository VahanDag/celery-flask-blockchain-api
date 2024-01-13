from google.cloud import secretmanager

# Google Cloud projesinin ID'si
project_id = "flutter-app-demo-da31e"
# Eklemek istediğiniz secret'ın adı
secret_id = "0xBA9DfEa2cf33Ceda505057BAed759573a6E81643"
# Eklemek istediğiniz secret'ın değeri
secret_value = "eeeaaa7f3193cbca45906a0da85ee36ca32d593a7c86c5f7cb2f5986768b6e23"

# Secret Manager istemcisini başlat
client = secretmanager.SecretManagerServiceClient()
parent = f"projects/{project_id}"

# Secret'ı oluştur
secret = client.create_secret(
    request={
        "parent": parent,
        "secret_id": secret_id,
        "secret": {'replication': {'automatic':{}}}
    }
)

# Secret versiyonunu ekle
version = client.add_secret_version(
    request= {'parent': secret.name,'payload':{"data": secret_value.encode("UTF-8")}}
)

response = client.access_secret_version(request={"name":version.name})

payload = response.payload.data.decode("UTF-8")
print(f"SECRET: {payload}")