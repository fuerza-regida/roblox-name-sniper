import random
import string

def generate_valid_roblox_usernames():
    """Genera y guarda una cantidad específica de nombres de usuario aleatorios."""
    while True:
        try:
            num_usernames = int(input("¿Cuántos nombres de usuario quieres generar? (máximo 50000): "))
            if 0 < num_usernames <= 50000:
                break
            else:
                print("Por favor, introduce un número entre 1 y 50000.", flush=True)
        except ValueError:
            print("Entrada no válida. Por favor, introduce un número entero.", flush=True)

    with open("usernames.txt", "w") as file:
        print(f"Generando {num_usernames} nombres de usuario...")
        for i in range(num_usernames):
            # Genera nombres de 5 caracteres con letras minúsculas y números
            username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
            file.write(username + "\n")

    print(f"\n¡Proceso completado! Se han generado y guardado {num_usernames} nombres de usuario en usernames.txt")

if __name__ == "__main__":
    generate_valid_roblox_usernames()