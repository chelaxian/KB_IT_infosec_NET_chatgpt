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

Эти команды покрывают все основные преобразования сертификатов между популярными форматами. Если есть еще какие-либо конкретные случаи, которые тебя интересуют, дай знать!
