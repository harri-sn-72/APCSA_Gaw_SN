
public class LivingNugget extends Enemy
{
    private int bounces;

    public LivingNugget()
    {
        super("Living Nugget", 30, "images/nugget.png");
        bounces = 0;
    }

    public void attack(Player p, Companion c)
    {
        bounces = bounces + 1;
        int dmg = 5 + bounces;
        dmg = c.blockDamage(dmg);
        p.takeDamage(dmg);
        System.out.println(name + " bounces and hits for " + dmg);

        health = health + 3;
        if (health > maxHealth)
        {
            health = maxHealth;
        }
        System.out.println(name + " eats crumbs (+3 HP).");
    }
}
