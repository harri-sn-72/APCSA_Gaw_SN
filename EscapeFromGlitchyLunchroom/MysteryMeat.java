import java.util.Random;

public class MysteryMeat extends Enemy
{
    private Random rand;

    public MysteryMeat()
    {
        super("Mystery Meat", 50, "images/mystery-meat.png");
        rand = new Random();
    }

    public void attack(Player p, Companion c)
    {
        int roll = rand.nextInt(10);
        if (roll <= 2)
        {
            System.out.println(name + " missed!");
            return;
        }
        if (roll >= 8)
        {
            int dmg = 15;
            dmg = c.blockDamage(dmg);
            p.takeDamage(dmg);
            System.out.println(name + " CRIT for " + dmg);
            return;
        }
        int dmg = 6 + roll;
        dmg = c.blockDamage(dmg);
        p.takeDamage(dmg);
        System.out.println(name + " hits for " + dmg);
    }
}
