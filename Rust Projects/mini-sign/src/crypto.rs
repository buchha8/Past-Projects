use ed25519_dalek::{
    Signature,
    Signer,
    Verifier,
    SigningKey,
    VerifyingKey,
};

use rand::rngs::OsRng;
use std::fs;


pub fn generate_keypair() -> (SigningKey, VerifyingKey) {
    let mut rng = OsRng;

    let signing_key = SigningKey::generate(&mut rng);
    let verifying_key = signing_key.verifying_key();

    (signing_key, verifying_key)
}


pub fn save_private_key(
    key: &SigningKey,
    filename: &str,
) -> Result<(), std::io::Error> {
    fs::write(
        filename,
        key.to_bytes(),
    )
}


pub fn save_public_key(
    key: &VerifyingKey,
    filename: &str,
) -> Result<(), std::io::Error> {
    fs::write(
        filename,
        key.to_bytes(),
    )
}


pub fn sign_file(
    key: &SigningKey,
    filename: &str,
) -> Result<Signature, std::io::Error> {
    let data = fs::read(filename)?;

    let signature = key.sign(&data);

    Ok(signature)
}


pub fn verify_file(
    key: &VerifyingKey,
    filename: &str,
    signature: &Signature,
) -> Result<bool, std::io::Error> {

    let data = fs::read(filename)?;

    let result = key.verify(
        &data,
        signature,
    );

    Ok(result.is_ok())
}


pub fn load_private_key(
    filename: &str,
) -> Result<SigningKey, std::io::Error> {

    let bytes = fs::read(filename)?;

    let key_bytes: [u8; 32] =
        bytes.try_into()
            .map_err(|_| {
                std::io::Error::new(
                    std::io::ErrorKind::InvalidData,
                    "Invalid private key length",
                )
            })?;

    Ok(SigningKey::from_bytes(&key_bytes))
}


pub fn load_public_key(
    filename: &str,
) -> Result<VerifyingKey, std::io::Error> {

    let bytes = fs::read(filename)?;

    let key_bytes: [u8; 32] =
        bytes.try_into()
            .map_err(|_| {
                std::io::Error::new(
                    std::io::ErrorKind::InvalidData,
                    "Invalid public key length",
                )
            })?;

    VerifyingKey::from_bytes(&key_bytes)
        .map_err(|_| {
            std::io::Error::new(
                std::io::ErrorKind::InvalidData,
                "Invalid public key",
            )
        })
}


pub fn load_signature(
    filename: &str,
) -> Result<Signature, std::io::Error> {

    let bytes = fs::read(filename)?;

    let signature_bytes: [u8; 64] =
        bytes.try_into()
            .map_err(|_| {
                std::io::Error::new(
                    std::io::ErrorKind::InvalidData,
                    "Invalid signature length",
                )
            })?;

    Ok(Signature::from_bytes(&signature_bytes))
}