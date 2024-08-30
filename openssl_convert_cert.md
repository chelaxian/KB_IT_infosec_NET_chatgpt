Вот список команд для использования OpenSSL для преобразования сертификатов между всеми популярными форматами:

### Основные расширения сертификатов:

1. **PEM** (`.pem`, `.crt`, `.cer`)
2. **DER** (`.der`)
3. **PFX/P12** (`.pfx`, `.p12`)
4. **PKCS#7/P7B** (`.p7b`, `.p7c`)

### Конвертация между форматами с использованием OpenSSL

#### 1. Конвертация **PEM** в другие форматы

- **PEM → DER:**

  ```bash
  openssl x509 -in certificate.pem -outform der -out certificate.der
  ```

- **PEM → PFX/P12:**

  ```bash
  openssl pkcs12 -export -out certificate.pfx -inkey privateKey.pem -in certificate.pem -certfile ca-bundle.pem
  ```

  > Здесь `privateKey.pem` — это ваш приватный ключ, а `ca-bundle.pem` — дополнительный промежуточный сертификат (если есть).

- **PEM → PKCS#7/P7B:**

  ```bash
  openssl crl2pkcs7 -nocrl -certfile certificate.pem -out certificate.p7b -certfile ca-bundle.pem
  ```

#### 2. Конвертация **DER** в другие форматы

- **DER → PEM:**

  ```bash
  openssl x509 -in certificate.der -inform der -out certificate.pem -outform pem
  ```

- **DER → PFX/P12:**

  ```bash
  openssl pkcs12 -export -in certificate.der -inkey privateKey.pem -out certificate.pfx
  ```

- **DER → PKCS#7/P7B:**

  ```bash
  openssl crl2pkcs7 -nocrl -certfile certificate.der -out certificate.p7b
  ```

#### 3. Конвертация **PFX/P12** в другие форматы

- **PFX/P12 → PEM:**

  ```bash
  openssl pkcs12 -in certificate.pfx -out certificate.pem -nodes
  ```

- **PFX/P12 → DER:**

  ```bash
  openssl pkcs12 -in certificate.pfx -out certificate.der -nodes -outform DER
  ```

- **PFX/P12 → PKCS#7/P7B:**

  ```bash
  openssl pkcs12 -in certificate.pfx -out temp.pem -nodes
  openssl crl2pkcs7 -nocrl -certfile temp.pem -out certificate.p7b
  ```

  > Сначала конвертируем в PEM, затем в PKCS#7/P7B.

#### 4. Конвертация **PKCS#7/P7B** в другие форматы

- **PKCS#7/P7B → PEM:**

  ```bash
  openssl pkcs7 -print_certs -in certificate.p7b -out certificate.pem
  ```

- **PKCS#7/P7B → DER:**

  ```bash
  openssl pkcs7 -inform PEM -outform DER -in certificate.p7b -out certificate.der
  ```

- **PKCS#7/P7B → PFX/P12:**

  ```bash
  openssl pkcs7 -print_certs -in certificate.p7b -out temp.pem
  openssl pkcs12 -export -in temp.pem -out certificate.pfx
  ```

  > Сначала конвертируем в PEM, затем в PFX/P12.

### Примечания:

1. **Путь к файлам:** Всегда указывайте полный или относительный путь к файлам сертификатов и ключей, чтобы избежать ошибок.
2. **Пароли:** Если PFX/P12 файл защищен паролем, OpenSSL запросит его при выполнении команд.
3. **Использование CA сертификатов:** При конвертации в некоторые форматы, например, в PFX/P12 или PKCS#7, может потребоваться указание дополнительных сертификатов (например, корневых или промежуточных).

Файлы с расширениями `.cer` и `.crt` по сути являются одинаковыми и представляют собой сертификаты в формате PEM или DER. Разница лишь в расширении файла, а не в содержимом. 

### Конвертация из **CER** в **CRT**

1. Если файл `.cer` уже в формате PEM, его достаточно просто переименовать:

    ```bash
    mv certificate.cer certificate.crt
    ```

2. Если файл `.cer` в формате DER, его нужно преобразовать в PEM:

    ```bash
    openssl x509 -in certificate.cer -inform der -out certificate.crt -outform pem
    ```

### Определение формата `.cer`

Чтобы определить, в каком формате `.cer` файл (PEM или DER), можно использовать следующую команду:

```bash
openssl x509 -in certificate.cer -noout -text
```

- Если сертификат читается в текстовом виде, он в формате **PEM**.
- Если вы видите ошибки, вероятно, он в формате **DER**.

### Интерпретация результатов:

- **Если сертификат читается в текстовом виде**, то он в формате **PEM**.  
  Пример вывода для PEM формата:

  ```
  Certificate:
      Data:
          Version: 3 (0x2)
          Serial Number:
              ...
      Signature Algorithm: sha256WithRSAEncryption
          Issuer: CN = ...
          ...
  ```

- **Если вы получите сообщение об ошибке или видите "unable to load certificate"**, то, вероятно, сертификат в формате **DER**.  

  Ошибка будет выглядеть примерно так:

  ```
  unable to load certificate
  140735125509952:error:0906D06C:PEM routines:PEM_read_bio:no start line:pem_lib.c:707:Expecting: TRUSTED CERTIFICATE
  ```

В случае если ваш сертификат в формате DER, вы можете конвертировать его в PEM с помощью следующей команды:

```bash
openssl x509 -in certificate.cer -inform der -out certificate.pem -outform pem
```
