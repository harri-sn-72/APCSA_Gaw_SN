
public class Enemy
{
    protected String name;
    protected int health;
    protected int maxHealth;
    protected String imageFile;

    public Enemy(String n, int hp, String img)
    {
        name = n;
        health = hp;
        maxHealth = hp;
        imageFile = img;
    }

    public String getName()
    {
        return name;
    }

    public int getHealth()
    {
        return health;
    }

    public int getMaxHealth()
    {
        return maxHealth;
    }

    public String getImageFile()
    {
        return imageFile;
    }

    public boolean isAlive()
    {
        return health > 0;
    }

    public void takeDamage(int dmg)
    {
        health = health - dmg;
        if (health < 0)
        {
            health = 0;
        }
    }

    public void attack(Player p, Companion c)
    {
        int dmg = 8;
        dmg = c.blockDamage(dmg);
        p.takeDamage(dmg);
    }
}
