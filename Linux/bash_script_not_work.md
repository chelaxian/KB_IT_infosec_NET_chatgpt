error

```bash
bash /mnt/c/RUN.sh
/: line 2: $'\r': command not found
/: line 4: $'\r': command not found
/: line 6: $'\r': command not found
/: eval: line 28: syntax error: unexpected end of file
/: eval: line 22: syntax error: unexpected end of file
/: line 9: $'\r': command not found
/: line 11: $'\r': command not found
```

fix

```bash
sudo apt update
sudo apt install dos2unix -y
sudo dos2unix /mnt/c/RUN.sh
```

```bash
bash /mnt/c/RUN.sh
```
