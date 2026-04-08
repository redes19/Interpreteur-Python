# Tests de l'interpréteur

## Assignation et print

x = 5; print(x);

// Affiche : 5

## Opérations arithmétiques

x = 3 + 2; print(x);

// Affiche : 5

x = 10 / 2; print(x);

// Affiche : 5.0

x = 4 * 3; print(x);

// Affiche : 12

x = 10 - 3; print(x);

// Affiche : 7

## Incrémentation

x = 5; x++; print(x);

// Affiche : 6

## Conditions

if simple :
x = 5; if(x > 3) { print(1); }

// Affiche : 1

if/else :
x = 2; if(x > 3) { print(1); } else { print(0); }

// Affiche : 0

elif — résultat 1 :
x = 1; if(x == 1) { print(1); } elif(x == 2) { print(2); } else { print(0); }

// Affiche : 1

elif — résultat 2 :
x = 2; if(x == 1) { print(1); } elif(x == 2) { print(2); } else { print(0); }

// Affiche : 2

elif — résultat else :
x = 5; if(x == 1) { print(1); } elif(x == 2) { print(2); } else { print(0); }

// Affiche : 0

## Opérateurs logiques

x = 5; if(x > 3 & x < 10) { print(1); }

// Affiche : 1

x = 1; if(x == 0 | x == 1) { print(1); }

// Affiche : 1

x = 15; if(x > 3 & x < 10) { print(1); }

// N'affiche rien

x = 10; if(x == 0 | x == 1) { print(1); }

// N'affiche rien

## Boucles

while :
x = 1; while(x <= 3) { print(x); x++; }

// Affiche :
// 1
// 2
// 3

for :
for(i = 0; i < 5; i++) { print(i); }

// Affiche :
// 0
// 1
// 2
// 3
// 4

## Fonctions

sans paramètre ni return :
fonction bonjour() { print(42); } bonjour();

// Affiche : 42

sans paramètre avec return :
fonction dix() { return 10; } x = dix(); print(x);

// Affiche : 10

avec paramètre :
fonction double(n) { return n * 2; } print(double(5));

// Affiche : 10

## Pile des contextes

variable locale n'écrase pas le global :
fonction test() { x = 99; print(x); } x = 1; test(); print(x);
// Affiche :
// 99
// 1

## Tableaux

tableau vide :
t = []; print(t);

// Affiche : []

tableau avec valeurs :
t = [1, 2, 3]; print(t);

// Affiche : [1, 2, 3]

modification par index :
t = [10, 20, 30]; t[1] = 99; print(t);

// Affiche : [10, 99, 30]

accès par index :
t = [10, 20, 30]; print(t[1]);

// Affiche : 20

longueur :
t = [10, 20, 30]; print(len.t);

// Affiche : 3

push :
t = [10, 20, 30]; push(t, 40); print(t);

// Affiche : [10, 20, 30, 40]

pop sans récupération :
t = [10, 20, 30]; pop(t); print(t);

// Affiche : [10, 20]

pop avec récupération :
t = [10, 20, 30]; print(pop(t));

// Affiche : 30

tableau passé en paramètre :
fonction f(a) { push(a, 100); print(a[2]); } t = [1, 2]; f(t); print(t);

// Affiche :
// 100
// [1, 2, 100]