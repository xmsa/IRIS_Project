source .env
dvc remote add -d -f $dvc__remote_name $dvc__remote_url
dvc remote modify $dvc__remote_name endpointurl $dvc__endpoint_url
dvc remote modify $dvc__remote_name use_ssl $minio__secure
dvc remote modify --local $dvc__remote_name access_key_id $minio__access_key
dvc remote modify --local $dvc__remote_name secret_access_key $minio__secret_key
