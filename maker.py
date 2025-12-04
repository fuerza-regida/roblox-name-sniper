import random
import string

def generate_valid_roblox_usernames():
    """generator"""
    while True:
        try:
            num_usernames = int(input("How many usernames do you want to generate? (maximum 50000): "))
            if 0 < num_usernames <= 50000:
                break
            else:
                print("Please enter a number between 1 and 50000.", flush=True)
        except ValueError:
            print("Entrada no válida. Por favor, introduce un número entero.", flush=True)

    with open("usernames.txt", "w") as file:
        print(f"Generating {num_usernames} usernames...")
        for i in range(num_usernames):
            # Genera nombres de 5 caracteres con letras minúsculas y números
            username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))
            file.write(username + "\n")

    print(f"\n¡Process complete! Files have been generated and saved. {num_usernames} usernames in usernames.txt")

if __name__ == "__main__":
    generate_valid_roblox_usernames()
