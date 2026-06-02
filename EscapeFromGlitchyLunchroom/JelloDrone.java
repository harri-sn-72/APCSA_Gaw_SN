
public class JelloDrone extends Enemy
{
    private boolean canDodge;

    public JelloDrone()
    {
        super("Jello Drone", 40, "images/jello-drone.png");
        canDodge = true;
    }

    public boolean dodged()
    {
        if (canDodge)
        {
            canDodge = false;
            System.out.println(name + " wobbled away!");
            return true;
        }
        canDodge = true;
        return false;
    }

    public void attack(Player p, Companion c)
    {
        int dmg = 5 + p.getTile();
        if (dmg > 12)
        {
            dmg = 12;
        }
        dmg = c.blockDamage(dmg);
        p.takeDamage(dmg);
        System.out.println(name + " zaps for " + dmg);
    }
}
