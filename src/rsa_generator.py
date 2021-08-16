from Crypto.PublicKey import RSA 

''' Generate RSA key pair '''
def generate_keys():
    # generate RSA key that 4096 bits long
    new_key = RSA.generate(4096) 
    # Export the Key in PEM format, the PEM extension contains ASCII encoding
    public_key = new_key.publickey().exportKey("PEM") 
    private_key = new_key.exportKey("PEM") 
    print(private_key.decode())
    print(public_key.decode())
    with open('private.pem' , 'w+') as f:
        f.write(private_key.decode())

    with open('public.pem' , 'w+') as f:
        f.write(public_key.decode())
    

if __name__ == "__main__":
    generate_keys()