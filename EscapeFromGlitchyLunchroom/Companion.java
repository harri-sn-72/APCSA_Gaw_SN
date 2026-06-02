
public class Companion
{
    private String name;
    private int helpPoints;
    private boolean ready;

    public Companion()
    {
        name = "Debug Duck";
        helpPoints = 3;
        ready = true;
    }

    public String getName()
    {
        return name;
    }

    public int helpAttack(Player p)
    {
        if (!ready)
        {
            return 0;
        }
        if (helpPoints > 0)
        {
            helpPoints = helpPoints - 1;
            System.out.println(name + " adds 4 bonus damage.");
            return 4;
        }
        return 0;
    }

    public int blockDamage(int dmg)
    {
        if (!ready)
        {
            return dmg;
        }
        int blocked = dmg / 2;
        System.out.println(name + " blocks " + blocked + " damage.");
        return dmg - blocked;
    }

    public void healPlayer(Player p)
    {
        if (helpPoints == 0)
        {
            p.heal(10);
            System.out.println(name + " shares a bread crust (+10 HP).");
            helpPoints = 2;
        }
    }
}
