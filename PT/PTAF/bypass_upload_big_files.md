## Bypass Upload Big Files >1GB+

### Для сервисов MS OneDrive / MS SharePoint

**PTAF PRO** в режиме **Prevent/Detect** имеет лимит на загрузку файла до **10 мегабайт**. \
В режиме **"Без мер защиты"** захардкоженный лимит до **1 гигабайта**. 

Для загрузки файлов в MS OneDrive / MS SharePoint используются следующие методы API-вызовов:
- StartUploadFile
- ContinueUpload
- FinishUpload
- GetUploadStatus
- CancelUpload

Вот такие регулярные выражения на **PTAF-AGENT** (стоящего в качестве балансировщика (см. [статью](https://github.com/chelaxian/KB_IT_infosec_NET_chatgpt/blob/main/PT/PTAF/ptaf_agent.nginx.conf.md)) перед **PTAF PRO**) для байпасса мимо **PTAF** на оригинальный бэкэнд на каждый из 5 метод помогли обойти эти ограничения:

nginx.conf:
```nginx
	#####################
	# OneDrive          #
	#####################
	
	# 1. URL:
	location ~* "^/sites/[^/]+/_api/web/GetFolderById\(@[a-z0-9]+\)/Files/AddStubUsingPath\(DecodedUrl=@[a-z0-9]+\)/StartUploadFile\(uploadId=@[a-z0-9]+\)$" {
		proxy_pass https://$orig_backend_site;
		include /opt/ptaf/conf/proxy-common.conf;
	}
	
	# 2. URL:
	location ~* "^/sites/[^/]+/_api/web/GetFileByServerRelativePath\(DecodedUrl=@[a-z0-9]+\)/ContinueUpload\(uploadId=@[a-z0-9]+,fileOffset=@[a-z0-9]+\)$" {
		proxy_pass https://$orig_backend_site;
		include /opt/ptaf/conf/proxy-common.conf;
	}
	
	# 3. URL:
	location ~* "^/sites/[^/]+/_api/web/GetFileByServerRelativePath\(DecodedUrl=@[a-z0-9]+\)/GetUploadStatus\(uploadId=@[a-z0-9]+\)$" {
		proxy_pass https://$orig_backend_site;
		include /opt/ptaf/conf/proxy-common.conf;
	}
	
	# 4. URL:
	location ~* "^/sites/[^/]+/_api/web/GetFileByServerRelativePath\(DecodedUrl=@[a-z0-9]+\)/CancelUpload\(uploadId=@[a-z0-9]+\)$" {
		proxy_pass https://$orig_backend_site;
		include /opt/ptaf/conf/proxy-common.conf;
	}
	
	# 5. URL:
	location ~* "^/sites/[^/]+/_api/web/GetFileByServerRelativePath\(DecodedUrl=@[a-z0-9]+\)/FinishUpload\(uploadId=@[a-z0-9]+,fileOffset=@[a-z0-9]+\)$" {
		proxy_pass https://$orig_backend_site;
		include /opt/ptaf/conf/proxy-common.conf;
	}
	
	
	#######################
	# SharePoint          #
	#######################
	
	# 6. URL:
	location ~* "^/sites/[^/]+/_api/web/GetFolderByServerRelativePath\(DecodedUrl=@[a-z0-9]+\)/Files/AddStubUsingPath\(DecodedUrl=@[a-z0-9]+\)/StartUploadFile\(uploadId=@[a-z0-9]+\)$" {
		proxy_pass https://$orig_backend_site;
		include /opt/ptaf/conf/proxy-common.conf;
	}
	
	# Для SharePoint остальные URI с методами (ContinueUpload, GetUploadStatus, CancelUpload, FinishUpload)
	# идентичны по шаблону с используемым GetFileByServerRelativePath и поэтому покрываются блоками 2, 3, 4 и 5 выше.
	
	
	#####################
	# Universal RegEx   #
	#####################
	
	# 7. Универсальный блок для всех случаев,
	# когда параметры в круглых скобках могут быть произвольными (любые допустимые значения).
	location ~* "^/sites/[^/]+/_api/web/(?:GetFolderById|GetFileByServerRelativePath|GetFolderByServerRelativePath)\([^)]*\)(?:/Files/AddStubUsingPath\([^)]*\))?/(?:StartUploadFile|ContinueUpload|FinishUpload|GetUploadStatus|CancelUpload)\([^)]*\)$" {
		proxy_pass https://$orig_backend_site;
		include /opt/ptaf/conf/proxy-common.conf;
	}
```
proxy-common.conf:
```conf
proxy_http_version 1.1;
proxy_request_buffering off;
proxy_buffering off;
proxy_set_header Host $host;
proxy_set_header Connection "";
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header Upgrade $http_upgrade;
proxy_pass_header Date;
proxy_pass_header Server;
proxy_ssl_server_name on;
proxy_ssl_name $ssl_server_name;
proxy_ssl_protocols TLSv1.2 TLSv1.3;
proxy_ssl_ciphers ALL:@SECLEVEL=0;
proxy_ssl_verify on;
proxy_ssl_verify_depth 1;
proxy_ssl_trusted_certificate /certs/root+intermediate.crt;

# Добавленные настройки для улучшения обработки больших файлов
client_body_timeout 3600s;
client_max_body_size 0;
proxy_max_temp_file_size 0;
proxy_connect_timeout 600s;
proxy_ignore_client_abort off;

# Настройки для Sharepoint/OneDrive
proxy_read_timeout 3600s;
proxy_send_timeout 3600s;
proxy_set_header Authorization $http_authorization;
```
