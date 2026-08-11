# Script Python bénin d'exemple — contenu simple et non dangereux
def greet(name):
    message = "Bonjour, " + name + "!"
    print(message)
    return message

def factorial(n):
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    user = "Etudiant"
    greet(user)
    print("5! =", factorial(5))
