## English 
This encryption and decryption algorithmwan an accidental idea that ocurred to me when I was researching how to be lazy nd quickly figure out how to solve a Rubik's Cube with a computer. It can also be considered a personal hobby.
Usage of Direct Use:
  CubeEncryptUtils_Python.py -mode encrypt -s "something you don't want others to know" -k location_to_save_key.key -o encrypt_msg
  CubeEncryptUtils_Python.py -mode encrypt -f input -k location_to_save_key.key -o encrypt_msg
  CubeEncryptUtils_Python.py -mode decrypt -f input -k key_file.key -o decrypt_msg
The Another File，CubeKeyEncoder.py，was 100% written by AI. It's used for convert the text into key file into a num string.
The Usage is:
  python CubeKeyEncoder.py encode -i key1.key -o encoded_keys.json --scheme xor
  python CubeKeyEncoder.py decode -i encoded_keys.json -o decoded_keys.json
  python CubeKeyEncoder.py encode -i key1.key -o keys.b64 --format base64
## 中文
