import rsa

pub, priv = rsa.newkeys(1024)

with open("rsa/public.pem", "wb") as f:
    f.write(pub.save_pkcs1("PEM")) 

with open("rsa/private.pem", "wb") as f:
    f.write(priv.save_pkcs1("PEM")) 