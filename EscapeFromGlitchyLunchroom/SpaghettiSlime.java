
public class SpaghettiSlime extends Enemy
{
    public SpaghettiSlime()
    {
        super("Spaghetti Slime", 45, "images/spaghetti-slime.png");
    }

    public void attack(Player p, Companion c)
    {
        System.out.println(name + " splashes noodles!");
        int dmg1 = 7;
        int dmg2 = 5;
        dmg1 = c.blockDamage(dmg1);
        p.takeDamage(dmg1);
        System.out.println("  hit 1: " + dmg1);
        if (p.isAlive())
        {
            dmg2 = c.blockDamage(dmg2);
            p.takeDamage(dmg2);
            System.out.println("  hit 2: " + dmg2);
        }
    }
}
