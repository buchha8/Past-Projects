mod crypto;

use std::env;


fn main() -> Result<(), Box<dyn std::error::Error>> {

    let args: Vec<String> = env::args().collect();


    if args.len() < 2 {
        println!("Usage:");
        println!("  cargo run -- generate-keys");
        println!("  cargo run -- sign <file>");
        println!("  cargo run -- verify <file> <signature>");

        return Ok(());
    }


    match args[1].as_str() {

        "generate-keys" => {
            let (private_key, public_key) =
                crypto::generate_keypair();


            crypto::save_private_key(
                &private_key,
                "keys/private.key",
            )?;


            crypto::save_public_key(
                &public_key,
                "keys/public.key",
            )?;


            println!("Keys generated!");
        }


        "sign" => {
            if args.len() < 3 {
                println!("Missing file path");
                return Ok(());
            }


            let private_key =
                crypto::load_private_key(
                    "keys/private.key"
                )?;


            let signature =
                crypto::sign_file(
                    &private_key,
                    &args[2],
                )?;


            std::fs::write(
                "signatures/message.sig",
                signature.to_bytes(),
            )?;


            println!("File signed!");
        }


        "verify" => {
            if args.len() < 4 {
                println!("Missing arguments");
                return Ok(());
            }


            let public_key =
                crypto::load_public_key(
                    "keys/public.key"
                )?;


            let signature =
                crypto::load_signature(
                    &args[3],
                )?;


            let valid =
                crypto::verify_file(
                    &public_key,
                    &args[2],
                    &signature,
                )?;


            println!(
                "Signature valid: {}",
                valid
            );
        }


        _ => {
            println!("Unknown command");
        }
    }


    Ok(())
}