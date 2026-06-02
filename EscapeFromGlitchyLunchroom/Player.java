
public class Player
{
    private String name;
    private int health;
    private int maxHealth;
    private int score;
    private int tile;
    private int patchUses;

    public Player(String n)
    {
        name = n;
        maxHealth = 100;
        health = maxHealth;
        score = 0;
        tile = 1;
        patchUses = 2;
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

    public int getScore()
    {
        return score;
    }

    public int getTile()
    {
        return tile;
    }

    public boolean isAlive()
    {
        if (health > 0)
        {
            return true;
        }
        return false;
    }

    public void addScore(int pts)
    {
        score = score + pts;
    }

    public void move()
    {
        if (tile < 5)
        {
            tile = tile + 1;
        }
    }

    public int getPatchUses()
    {
        return patchUses;
    }

    public int normalAttack()
    {
        return 10;
    }

    public int patchAttack()
    {
        if (patchUses <= 0)
        {
            System.out.println("No patches left.");
            return normalAttack();
        }
        patchUses = patchUses - 1;
        System.out.println(name + " uses Code Patch!");
        return 20;
    }

    public void takeDamage(int dmg)
    {
        health = health - dmg;
        if (health < 0)
        {
            health = 0;
        }
    }

    public void heal(int amt)
    {
        health = health + amt;
        if (health > maxHealth)
        {
            health = maxHealth;
        }
    }

    public void printStats()
    {
        System.out.println(name + " HP:" + health + "/" + maxHealth
            + " Score:" + score + " Tile:" + tile);
    }
}
