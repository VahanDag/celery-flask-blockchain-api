

from celery_flask import clientSecret, project_id, redis_init, w3_init

admin_addresses = ["0xE25eD8b08296aC41EbFD0987CbcAe5f30D67A82c", "0x040dF6198086b2FA8a452e592046a451fE173721", "0xBA9DfEa2cf33Ceda505057BAed759573a6E81643"]


def get_address_private_nonce(current_admin_index):
    worker_admin = admin_addresses[current_admin_index]
    secret_address_path = f"projects/{project_id}/secrets/{worker_admin}/versions/latest"
    response_secret = clientSecret.access_secret_version(request={"name":secret_address_path})
    worker_admin_private_key = response_secret.payload.data.decode("UTF-8")
    
    nonce = get_and_increment_nonce(worker_admin)
    
    return worker_admin, worker_admin_private_key, nonce

def get_next_admin_index():
    key = "current_admin_index"
    current_index = redis_init.get(key)
    if current_index is None:
        current_index = 0
    else:
        current_index = int(current_index)
    
    next_index = (current_index + 1) % len(admin_addresses)
    redis_init.set(key, next_index)
    return current_index



def get_and_increment_nonce(address):
    key = f"nonce:{address}"
    nonce = redis_init.get(key)
    if nonce is None:
        # Burada Ethereum ağından gerçek nonce değerini alın

        nonce = w3_init.eth.get_transaction_count(w3_init.to_checksum_address(address))
    else:
        nonce = int(nonce)
    # Nonce değerini arttır ve kaydet
    redis_init.set(key, nonce + 1)
    return nonce


def update_nonce(address):
    key= f"nonce:{address}"
    nonce = w3_init.eth.get_transaction_count(w3_init.to_checksum_address(address))
    redis_init.set(key,nonce)
