import java.util.Scanner;

public class greatPorridgeHeist {
       public static void main(String[] args) {
               Scanner scanner = new Scanner(System.in);

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
         
         } else if (character == 2) {
         System.out.println("Great choice for choosing Amanda. Now, type 1 to begin.");
                  int begin = scanner.nextInt();
         } else {
               System.exit(0);

         }
         
      } else {
      System.exit(0);
      }
   }
}
