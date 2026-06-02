import java.util.Random;

public class LunchLady3000 extends Enemy
{
    private boolean playerUsedPatch;
    private Random rand;

    public LunchLady3000()
    {
        super("Lunch Lady 3000", 100, "images/lunch-lady-3000.png");
        playerUsedPatch = false;
        rand = new Random();
    }

    public void setPlayerUsedPatch(boolean used)
    {
        playerUsedPatch = used;
    }

    public void attack(Player p, Companion c)
    {
        double percent = (double) health / maxHealth;

        if (percent > 0.5)
        {
            normalAttack(p, c);
        }
        else if (percent > 0.25)
        {
            specialAttack(p, c);
        }
        else
        {
            rageAttack(p, c);
        }
    }

    private void normalAttack(Player p, Companion c)
    {
        int dmg = 10;
        dmg = c.blockDamage(dmg);
        p.takeDamage(dmg);
        System.out.println(name + " ladles you for " + dmg);
    }

    private void specialAttack(Player p, Companion c)
    {
        System.out.println(name + " STEAM TRAY attack!");
        int i = 0;
        while (i < 3 && p.isAlive())
        {
            int dmg = 4 + rand.nextInt(4);
            dmg = c.blockDamage(dmg);
            p.takeDamage(dmg);
            System.out.println("  tray " + (i + 1) + " does " + dmg);
            i = i + 1;
        }
    }

    private void rageAttack(Player p, Companion c)
    {
        if (playerUsedPatch)
        {
            System.out.println(name + " counters your patch!");
            int dmg = 22;
            dmg = c.blockDamage(dmg);
            p.takeDamage(dmg);
            playerUsedPatch = false;
        }
        else
        {
            int dmg = 14 + rand.nextInt(5);
            dmg = c.blockDamage(dmg);
            p.takeDamage(dmg);
            System.out.println(name + " microwave blast " + dmg);
        }
    }
}
