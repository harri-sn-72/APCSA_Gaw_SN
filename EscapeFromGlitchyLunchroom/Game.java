import java.util.ArrayList;

public class Game
{
    private Player player;
    private Companion duck;
    private ArrayList<Enemy> enemies;
    private GameWindow window;
    private int level;
    private int enemyNum;
    private Enemy currentEnemy;
    private boolean won;
    private boolean waitingForNextLevel;

    public Game()
    {
        enemies = new ArrayList<Enemy>();
        level = 1;
        enemyNum = 0;
        won = false;
        waitingForNextLevel = false;
    }

    public static void main(String[] args)
    {
        Game g = new Game();
        g.start();
    }

    public void start()
    {
        window = new GameWindow(this);
        window.open();
    }

    public void beginGame(String playerName)
    {
        if (playerName.length() == 0)
        {
            playerName = "Student";
        }
        player = new Player(playerName);
        duck = new Companion();
        level = 1;
        enemyNum = 0;
        won = false;
        waitingForNextLevel = false;
        setupLevel(level);
        startNextFight();
        window.showBattleScreen();
        window.addLog("Welcome " + player.getName() + "! Click buttons to fight.");
    }

    public void setupLevel(int lvl)
    {
        enemies.clear();
        enemyNum = 0;

        if (lvl == 1)
        {
            enemies.add(new LivingNugget());
        }
        else if (lvl == 2)
        {
            enemies.add(new LivingNugget());
            enemies.add(new SpaghettiSlime());
        }
        else if (lvl == 3)
        {
            enemies.add(new MysteryMeat());
            enemies.add(new JelloDrone());
        }
        else if (lvl == 4)
        {
            enemies.add(new LunchLady3000());
        }
    }

    public void startNextFight()
    {
        if (enemyNum < enemies.size())
        {
            currentEnemy = enemies.get(enemyNum);
            waitingForNextLevel = false;
            window.addLog("Fight: " + currentEnemy.getName());
            window.refresh();
        }
    }

    public void clickAttack()
    {
        if (!canPlay())
        {
            return;
        }

        int dmg = player.normalAttack() + duck.helpAttack(player);
        hitEnemy(dmg);
        window.addLog("Attack for " + dmg + " damage.");
        enemyTurn();
        afterTurn();
    }

    public void clickMove()
    {
        if (!canPlay())
        {
            return;
        }

        int oldTile = player.getTile();
        player.move();
        if (player.getTile() > oldTile)
        {
            window.addLog("Moved to tile " + player.getTile());
        }
        else
        {
            window.addLog("Already at last tile.");
        }
        enemyTurn();
        afterTurn();
    }

    public void clickPatch()
    {
        if (!canPlay())
        {
            return;
        }

        if (currentEnemy instanceof LunchLady3000)
        {
            LunchLady3000 boss = (LunchLady3000) currentEnemy;
            boss.setPlayerUsedPatch(true);
        }
        int dmg = player.patchAttack();
        hitEnemy(dmg);
        window.addLog("Code Patch hits for " + dmg + ".");
        enemyTurn();
        afterTurn();
    }

    public void clickHeal()
    {
        if (!canPlay())
        {
            return;
        }

        player.heal(12);
        duck.healPlayer(player);
        window.addLog("Healed with granola bar.");
        enemyTurn();
        afterTurn();
    }

    public void clickNextLevel()
    {
        if (!waitingForNextLevel)
        {
            return;
        }

        if (level == 4 && won)
        {
            window.showWinScreen();
            return;
        }

        level = level + 1;
        setupLevel(level);
        startNextFight();
        window.addLog("Level " + level + " started!");
        window.refresh();
    }

    private void hitEnemy(int dmg)
    {
        if (currentEnemy instanceof JelloDrone)
        {
            JelloDrone j = (JelloDrone) currentEnemy;
            if (j.dodged())
            {
                window.addLog("Jello Drone dodged!");
                return;
            }
        }
        currentEnemy.takeDamage(dmg);
    }

    private void enemyTurn()
    {
        if (currentEnemy == null || !currentEnemy.isAlive() || !player.isAlive())
        {
            return;
        }

        int hpBefore = player.getHealth();
        currentEnemy.attack(player, duck);
        int lost = hpBefore - player.getHealth();
        if (lost > 0)
        {
            window.addLog(currentEnemy.getName() + " hit you for " + lost + ".");
        }
    }

    private void afterTurn()
    {
        window.refresh();

        if (!player.isAlive())
        {
            window.showLoseScreen();
            return;
        }

        if (!currentEnemy.isAlive())
        {
            int pts = 20 + level * 5;
            player.addScore(pts);
            window.addLog("Enemy defeated! +" + pts + " points.");
            enemyNum = enemyNum + 1;

            if (enemyNum < enemies.size())
            {
                startNextFight();
            }
            else
            {
                checkLevelDone();
            }
        }
    }

    private void checkLevelDone()
    {
        if (passedLevel())
        {
            if (level == 4)
            {
                won = true;
                waitingForNextLevel = true;
                window.addLog("YOU WIN! Click button to play again.");
                window.showLevelDone(true);
            }
            else
            {
                waitingForNextLevel = true;
                window.addLog("Level clear! Score: " + player.getScore()
                    + ". Click Next Level.");
                window.showLevelDone(false);
            }
        }
        else
        {
            window.addLog("Need more points. Fight again on this level.");
            enemyNum = 0;
            setupLevel(level);
            startNextFight();
        }
    }

    private boolean passedLevel()
    {
        if (level == 1 && player.getScore() >= 30)
        {
            return true;
        }
        if (level == 2 && player.getScore() >= 60)
        {
            return true;
        }
        if (level == 3 && player.getScore() >= 90)
        {
            return true;
        }
        if (level == 4 && player.getScore() >= 120)
        {
            return true;
        }
        return false;
    }

    private boolean canPlay()
    {
        if (player == null || currentEnemy == null)
        {
            return false;
        }
        if (!player.isAlive() || !currentEnemy.isAlive())
        {
            return false;
        }
        if (waitingForNextLevel)
        {
            return false;
        }
        return true;
    }

    public Player getPlayer()
    {
        return player;
    }

    public Companion getDuck()
    {
        return duck;
    }

    public Enemy getCurrentEnemy()
    {
        return currentEnemy;
    }

    public int getLevel()
    {
        return level;
    }

    public boolean isWaitingForNextLevel()
    {
        return waitingForNextLevel;
    }
}
