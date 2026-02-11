// SN, Severson
// Great Porridge Heist - Fairy Tale Project
// Last modified: February 11, 2026 at 4:52 AM

import java.util.Scanner;

public class greatPorridgeHeist {
        public static void pause() {
        System.out.println("Press Enter to continue...");
        Scanner temp = new Scanner(System.in);
        temp.nextLine();
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        // Characteristic variables
        int tool = 0;           
        boolean speedHigh = false; 
        boolean greed = false;
        int stepsTaken = 0;     
        double magicLevel = 1.0;
           
        System.out.println("Welcome to the Great Porridge Heist!");
        System.out.println("Are you ready to get started? Type 0 to begin:");
        int start = scanner.nextInt();
        
        if (start == 0) {
            System.out.println("Welcome! Choose your character:");
            System.out.println("1. Chase - a fierce warrior that takes up any challenge.");
            System.out.println("2. Amanda - the guardian angel looking to defeat the evil.");
            int character = scanner.nextInt();
            
            if (character == 1) {
                System.out.println("Great choice for choosing Chase. Now, type 1 to begin.");
                int begin = scanner.nextInt();
                if (begin != 1) {
                    System.exit(0);
                }
            } else if (character == 2) {
                System.out.println("Great choice for choosing Amanda. Now, type 1 to begin.");
                int begin = scanner.nextInt();
                if (begin != 1) {
                    System.exit(0);
                }
            } else {
                System.exit(0);
            }
            
            pause();             
            System.out.println("\nSTART: The Beanstalk Base");
            System.out.println("You stand before a massive beanstalk reaching into the clouds.");
            System.out.println("1. Climb the Beanstalk");
            System.out.println("2. Try to fly");
            System.out.print("Your choice: ");
            int q1 = scanner.nextInt();
            stepsTaken++;
            
            if (q1 == 2) {
                System.out.println("You don't have wings and fall. Gravity wins.");
                System.exit(0);
            } else if (q1 != 1) {
                System.exit(0);
            }
            System.out.println("You climb the beanstalk successfully!");
            
            pause(); 
            
            System.out.println("\nThe Trail");
            System.out.println("You see a trail of breadcrumbs leading into the forest.");
            System.out.println("1. Follow the breadcrumbs");
            System.out.println("2. Eat the breadcrumbs");
            System.out.print("Your choice: ");
            int q2 = scanner.nextInt();
            stepsTaken++;
            
            if (q2 == 2) {
                System.out.println("The birds attack you for stealing their food. Game over.");
                System.exit(0);
            } else if (q2 != 1) {
                System.exit(0);
            }
            System.out.println("You wisely follow the trail...");
            
            pause(); 
            
        
            System.out.println("\nThe Bear Guards");
            System.out.println("Three bears block your path, looking menacing.");
            System.out.println("1. Bribe with Honey");
            System.out.println("2. Fight them");
            System.out.print("Your choice: ");
            int q3 = scanner.nextInt();
            stepsTaken++;
            
            if (q3 == 2) {
                System.out.println("Never bring a ladle to a bear fight.");
                System.exit(0);
            } else if (q3 != 1) {
                System.exit(0);
            }
            System.out.println("The bears accept your honey and let you pass!");
            
            pause(); 
            
            System.out.println("\nThe Tool Pick-up");
            System.out.println("You find two mystical items on a pedestal:");
            System.out.println("1. Magic Bean");
            System.out.println("2. Golden Feather");
            System.out.print("Which do you take? ");
            tool = scanner.nextInt();
            stepsTaken++;
            
            if (tool == 1) {
                System.out.println("You pocket the Magic Bean. It glows faintly.");
                magicLevel = 1.5; 
            } else if (tool == 2) {
                System.out.println("You take the Golden Feather. It feels light as air.");
                magicLevel = 1.2;  
            } else {
                System.exit(0);
            }
            
            pause(); 
                   
            System.out.println("\nThe Sleeping Giant");
            System.out.println("A massive giant sleeps in the hallway, snoring loudly.");
            System.out.println("1. Sneak past");
            System.out.println("2. Shout 'Fee-Fi-Fo-Fum!'");
            System.out.print("Your choice: ");
            int q5 = scanner.nextInt();
            stepsTaken++;
            
            if (q5 == 2) {
                System.out.println("He stepped on you. Flatly.");
                System.exit(0);
            } else if (q5 != 1) {
                System.exit(0);
            }
            System.out.println("You tiptoe past the sleeping giant successfully!");
            
            pause(); 
               
            System.out.println("\nThe Rescue");
            System.out.println("You find Hansel & Gretel trapped in a cage!");
            System.out.println("1. Save Hansel & Gretel");
            System.out.println("2. Leave them for the Oven");
            System.out.print("Your choice: ");
            int q6 = scanner.nextInt();
            stepsTaken++;
            
            if (q6 == 2) {
                System.out.println("You have no heart. The story ends in shame.");
                System.exit(0);
            } else if (q6 != 1) {
                System.exit(0);
            }
            System.out.println("You free them! They thank you and run to safety.");
            
            pause(); 
               
            System.out.println("\nThe Potion Room");
            System.out.println("You enter a room filled with bubbling potions.");
            System.out.println("1. Drink the first bottle.");
            System.out.println("2. Drink the second bottle.");
            System.out.print("Your choice: ");
            int q7 = scanner.nextInt();
            stepsTaken++;
            
            if (q7 == 1) {
                speedHigh = true;  
                System.out.println("Excellent choice. You feel a surge of energy! Speed increased!");
            } else if (q7 == 2) {
                speedHigh = false;  
                System.out.println("You decide to die today. Goodbye!");
            } else {
                System.exit(0);
            }
            
            pause();  
            
            System.out.println("\nThe Escape");
            System.out.println("You hear footsteps! The Giant is waking up!");
            System.out.println("1. Run for the Door");
            System.out.println("2. Hide in the Cupboard");
            System.out.print("Your choice: ");
            int q8 = scanner.nextInt();
            stepsTaken++;
            
            if (q8 == 2) {
                System.out.println("The Giant found you. You are now a side dish.");
                System.exit(0);
            } else if (q8 != 1) {
                System.exit(0);
            }
            System.out.println("You sprint toward the exit!");
            
            pause();  
               
            System.out.println("\nThe Treasure Choice");
            System.out.println("You pass a room full of golden eggs!");
            System.out.println("1. Grab the Gold Eggs");
            System.out.println("2. Leave the Gold");
            System.out.print("Your choice: ");
            int q9 = scanner.nextInt();
            stepsTaken++;
            
            if (q9 == 1) {
                greed = true; 
                System.out.println("You grab as many golden eggs as you can carry!");
            } else if (q9 == 2) {
                greed = false; 
                System.out.println("You resist the temptation and leave empty-handed.");
            } else {
                System.exit(0);
            }
            
            pause();  
               
            System.out.println("\nThe Beanstalk Descent");
            System.out.println("You reach the beanstalk and start climbing down!");
            
            if (greed && !speedHigh) {
                System.out.println("Too heavy! The Giant caught you.");
                System.exit(0);
            }
            
            System.out.println("You make it down safely!");
            
            pause();  
            int stepsCategory = stepsTaken / 3; 
            int stepsPattern = stepsTaken % 3;   
            double finalScore = stepsTaken * magicLevel;  
            
            System.out.println("\n THE END");
            System.out.println("Steps taken: " + stepsTaken);
            System.out.println("Final score: " + Math.round(finalScore));
                //CREDIT for Math.round function: StackOverflow https://stackoverflow.com/questions/13210491/math-round-java
            
            if (greed && speedHigh && tool == 1) {
               
                System.out.println("\nGREEDY VICTORY!");
                System.out.println("You escaped with the gold eggs AND your life!");
                System.out.println("The Magic Bean's power combined with your speed made you unstoppable.");
                System.out.println("You live in luxury forever, but sometimes wonder if it was worth it...");
            } else if (!greed && tool == 2) {
                
                System.out.println("\nPURE HERO!");
                System.out.println("You escaped without the treasure, but with your honor intact.");
                System.out.println("The Golden Feather granted you the gift of flight!");
                System.out.println("You return to help others in need, becoming a legendary hero!");
            } else {
           
                System.out.println("\nMODEST SUCCESS!");
                System.out.println("You survived the Great Porridge Heist!");
                System.out.println("Your journey taught you that courage matters more than gold.");
                System.out.println("You live happily ever after, telling tales of your adventure!");
            }
            
            
            if (stepsPattern == 0) {
                System.out.println("\nThe fairy gods smile upon you! Your steps were perfectly aligned.");
            }
            
        } else {
            System.exit(0);
        }
        
        scanner.close();
    }
}

