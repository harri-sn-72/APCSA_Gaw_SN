import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.FlowLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JProgressBar;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;

/**
 * The game screen you click and play on.
 * JButton listener help: https://stackoverflow.com/questions/3385933/how-do-i-add-an-action-listener-to-a-jbutton-in-java
 * Image in JLabel: https://stackoverflow.com/questions/21804131/how-to-display-pictures-in-java
 */
public class GameWindow implements ActionListener
{
    private Game game;
    private JFrame frame;

    private JPanel startPanel;
    private JPanel battlePanel;
    private JPanel endPanel;

    private JTextField nameBox;
    private JLabel playerPic;
    private JLabel enemyPic;
    private JLabel duckPic;
    private JLabel playerHpLabel;
    private JLabel enemyHpLabel;
    private JLabel infoLabel;
    private JProgressBar playerBar;
    private JProgressBar enemyBar;
    private JTextArea logArea;
    private JLabel[] tileLabels;

    private JButton attackBtn;
    private JButton moveBtn;
    private JButton patchBtn;
    private JButton healBtn;
    private JButton nextLevelBtn;

    public GameWindow(Game g)
    {
        game = g;
        frame = new JFrame("Escape from the Glitchy Lunchroom");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(900, 650);
        frame.setLocationRelativeTo(null);

        buildStartPanel();
        buildBattlePanel();
        buildEndPanel();

        frame.getContentPane().add(startPanel, BorderLayout.CENTER);
    }

    private void buildStartPanel()
    {
        startPanel = new JPanel();
        startPanel.setLayout(new GridLayout(6, 1));

        JLabel title = new JLabel("Escape from the Glitchy Lunchroom", JLabel.CENTER);
        JLabel story = new JLabel("The cafeteria is corrupted. Defeat the food!", JLabel.CENTER);
        nameBox = new JTextField("Student");
        JButton startBtn = new JButton("START GAME");
        startBtn.setActionCommand("start");
        startBtn.addActionListener(this);

        startPanel.add(title);
        startPanel.add(story);
        startPanel.add(new JLabel("Your name:", JLabel.CENTER));
        startPanel.add(nameBox);
        startPanel.add(startBtn);
        startPanel.add(new JLabel(" "));
    }

    private void buildBattlePanel()
    {
        battlePanel = new JPanel(new BorderLayout());

        JPanel top = new JPanel(new FlowLayout());
        infoLabel = new JLabel("Level 1");
        top.add(infoLabel);
        battlePanel.add(top, BorderLayout.NORTH);

        JPanel middle = new JPanel(new GridLayout(1, 3));
        playerPic = new JLabel("", JLabel.CENTER);
        duckPic = new JLabel("", JLabel.CENTER);
        enemyPic = new JLabel("", JLabel.CENTER);
        middle.add(playerPic);
        middle.add(duckPic);
        middle.add(enemyPic);
        battlePanel.add(middle, BorderLayout.CENTER);

        JPanel bars = new JPanel(new GridLayout(2, 2));
        playerHpLabel = new JLabel("Player HP");
        enemyHpLabel = new JLabel("Enemy HP");
        playerBar = new JProgressBar(0, 100);
        enemyBar = new JProgressBar(0, 100);
        playerBar.setStringPainted(true);
        enemyBar.setStringPainted(true);
        bars.add(playerHpLabel);
        bars.add(enemyHpLabel);
        bars.add(playerBar);
        bars.add(enemyBar);
        battlePanel.add(bars, BorderLayout.SOUTH);

        JPanel bottom = new JPanel(new BorderLayout());

        JPanel tiles = new JPanel(new FlowLayout());
        tileLabels = new JLabel[5];
        int t = 1;
        while (t <= 5)
        {
            tileLabels[t - 1] = new JLabel("[" + t + "]");
            tileLabels[t - 1].setOpaque(true);
            tileLabels[t - 1].setBackground(Color.LIGHT_GRAY);
            tileLabels[t - 1].setBorder(javax.swing.BorderFactory.createLineBorder(Color.BLACK));
            tiles.add(tileLabels[t - 1]);
            t = t + 1;
        }
        bottom.add(tiles, BorderLayout.NORTH);

        JPanel buttons = new JPanel(new FlowLayout());
        attackBtn = new JButton("ATTACK");
        moveBtn = new JButton("MOVE ->");
        patchBtn = new JButton("CODE PATCH");
        healBtn = new JButton("HEAL");
        nextLevelBtn = new JButton("NEXT LEVEL");
        attackBtn.setActionCommand("attack");
        moveBtn.setActionCommand("move");
        patchBtn.setActionCommand("patch");
        healBtn.setActionCommand("heal");
        nextLevelBtn.setActionCommand("nextlevel");
        attackBtn.addActionListener(this);
        moveBtn.addActionListener(this);
        patchBtn.addActionListener(this);
        healBtn.addActionListener(this);
        nextLevelBtn.addActionListener(this);
        nextLevelBtn.setEnabled(false);
        buttons.add(attackBtn);
        buttons.add(moveBtn);
        buttons.add(patchBtn);
        buttons.add(healBtn);
        buttons.add(nextLevelBtn);
        bottom.add(buttons, BorderLayout.CENTER);

        logArea = new JTextArea(6, 40);
        logArea.setEditable(false);
        JScrollPane scroll = new JScrollPane(logArea);
        bottom.add(scroll, BorderLayout.SOUTH);

        battlePanel.add(bottom, BorderLayout.PAGE_END);
    }

    private void buildEndPanel()
    {
        endPanel = new JPanel(new GridLayout(3, 1));
        JButton again = new JButton("PLAY AGAIN");
        again.setActionCommand("restart");
        again.addActionListener(this);
        endPanel.add(new JLabel(" ", JLabel.CENTER));
        endPanel.add(new JLabel("Game Over", JLabel.CENTER));
        endPanel.add(again);
    }

    public void open()
    {
        frame.setVisible(true);
    }

    public void showBattleScreen()
    {
        frame.getContentPane().removeAll();
        frame.getContentPane().add(battlePanel, BorderLayout.CENTER);
        frame.revalidate();
        frame.repaint();
        refresh();
    }

    public void showWinScreen()
    {
        endPanel.removeAll();
        endPanel.setLayout(new GridLayout(4, 1));
        endPanel.add(new JLabel("YOU ESCAPED THE LUNCHROOM!", JLabel.CENTER));
        endPanel.add(new JLabel("Final score: " + game.getPlayer().getScore(), JLabel.CENTER));
        JButton again = new JButton("PLAY AGAIN");
        again.setActionCommand("restart");
        again.addActionListener(this);
        endPanel.add(again);
        frame.getContentPane().removeAll();
        frame.getContentPane().add(endPanel, BorderLayout.CENTER);
        frame.revalidate();
        frame.repaint();
    }

    public void showLoseScreen()
    {
        endPanel.removeAll();
        endPanel.setLayout(new GridLayout(4, 1));
        endPanel.add(new JLabel("SYSTEM LOCKED", JLabel.CENTER));
        endPanel.add(new JLabel(game.getPlayer().getName() + " is trapped.", JLabel.CENTER));
        JButton again = new JButton("TRY AGAIN");
        again.setActionCommand("restart");
        again.addActionListener(this);
        endPanel.add(again);
        frame.getContentPane().removeAll();
        frame.getContentPane().add(endPanel, BorderLayout.CENTER);
        frame.revalidate();
        frame.repaint();
    }

    public void showLevelDone(boolean finalWin)
    {
        if (finalWin)
        {
            nextLevelBtn.setText("YOU WIN!");
        }
        else
        {
            nextLevelBtn.setText("NEXT LEVEL");
        }
        nextLevelBtn.setEnabled(true);
        attackBtn.setEnabled(false);
        moveBtn.setEnabled(false);
        patchBtn.setEnabled(false);
        healBtn.setEnabled(false);
    }

    public void addLog(String msg)
    {
        logArea.append(msg + "\n");
        logArea.setCaretPosition(logArea.getDocument().getLength());
    }

    public void refresh()
    {
        Player p = game.getPlayer();
        Enemy e = game.getCurrentEnemy();
        if (p == null)
        {
            return;
        }

        infoLabel.setText("Level " + game.getLevel() + " | Score " + p.getScore()
            + " | Tile " + p.getTile() + " | Patches " + p.getPatchUses());

        playerPic.setIcon(loadPic("images/student.png"));
        duckPic.setIcon(loadPic("images/rubber-duck.png"));

        if (e != null)
        {
            enemyPic.setIcon(loadPic(e.getImageFile()));
            enemyHpLabel.setText(e.getName() + " HP");
            enemyBar.setMaximum(e.getMaxHealth());
            enemyBar.setValue(e.getHealth());
        }

        playerHpLabel.setText(p.getName() + " HP");
        playerBar.setMaximum(p.getMaxHealth());
        playerBar.setValue(p.getHealth());

        updateTiles(p.getTile());

        if (game.isWaitingForNextLevel())
        {
            return;
        }

        boolean alive = p.isAlive() && e != null && e.isAlive();
        attackBtn.setEnabled(alive);
        moveBtn.setEnabled(alive);
        patchBtn.setEnabled(alive);
        healBtn.setEnabled(alive);
    }

    private void updateTiles(int playerTile)
    {
        int i = 0;
        while (i < 5)
        {
            int num = i + 1;
            tileLabels[i].setText("[" + num + "]");
            if (num == playerTile)
            {
                tileLabels[i].setBackground(Color.YELLOW);
            }
            else
            {
                tileLabels[i].setBackground(Color.LIGHT_GRAY);
            }
            i = i + 1;
        }
    }

    private ImageIcon loadPic(String path)
    {
        ImageIcon icon = new ImageIcon(path);
        if (icon.getIconWidth() > 0)
        {
            return new ImageIcon(icon.getImage().getScaledInstance(180, 180, java.awt.Image.SCALE_SMOOTH));
        }
        return icon;
    }

    public void actionPerformed(ActionEvent e)
    {
        String cmd = e.getActionCommand();

        if (cmd.equals("start"))
        {
            game.beginGame(nameBox.getText().trim());
            return;
        }

        if (cmd.equals("attack"))
        {
            game.clickAttack();
            return;
        }

        if (cmd.equals("move"))
        {
            game.clickMove();
            return;
        }

        if (cmd.equals("patch"))
        {
            game.clickPatch();
            return;
        }

        if (cmd.equals("heal"))
        {
            game.clickHeal();
            return;
        }

        if (cmd.equals("nextlevel"))
        {
            nextLevelBtn.setEnabled(false);
            attackBtn.setEnabled(true);
            moveBtn.setEnabled(true);
            patchBtn.setEnabled(true);
            healBtn.setEnabled(true);
            game.clickNextLevel();
            return;
        }

        if (cmd.equals("restart"))
        {
            logArea.setText("");
            frame.getContentPane().removeAll();
            frame.getContentPane().add(startPanel, BorderLayout.CENTER);
            frame.revalidate();
            frame.repaint();
        }
    }
}
