# Java Project Source Code Context

## 1. Project Structure
```text
src\module-info.java
src\my\MyDemo.java
src\my\MyFrame.java
src\my\MyFrame02.java
```

## 2. Source Code Files

### File: src\module-info.java
```java
/**
 * 
 */
/**
 * 
 */
module swing_0302 {
	requires java.desktop;
}
```

### File: src\my\MyDemo.java
```java
package my;

import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;

public class MyDemo {
	public static void main(String[] args) {
		// JFrame = a GUI window to add components to
				JFrame frame = new MyFrame02("Swing Example");

				// When the window closed, quit the application
				frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
				
				frame.setSize(400,300);
				frame.setVisible(true);


	}

}

```

### File: src\my\MyFrame.java
```java
package my;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.SimpleDateFormat;
import java.util.Date;

import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.SwingConstants;

public class MyFrame extends JFrame {

	// Create a label for show the time
	JLabel timeLabel = new JLabel("00:00:00");
	// Add a Text Field
	JTextField textField = new JTextField(20);
	// next button
	JButton nextButton = new JButton("Next");
	//Add a ComboBox
	JComboBox<String> colorField = new JComboBox<>();
	//Add a Label2
	JLabel label2 = new JLabel();

	public MyFrame(String title) {
		super(title);
		// create a container
		JPanel root = new JPanel();
		this.setContentPane(root);

		// Add something in the Panel
		JButton button = new JButton("Test");
		root.add(button);

		// Add a label to the panel
		JLabel label = new JLabel("Hello");
		root.add(label);

		root.add(timeLabel);

		root.add(textField);
		textField.setText("Hello, World!");

		// Add another button
		JButton button2 = new JButton("Get Text");
		root.add(button2);
		button2.addActionListener(new ActionListener() {

			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				getText();
			}
		});

		// Add a listener to the Button
		// ActionListener listener = new MyActionListener();
		button.addActionListener(e -> showTime());
		
		//Add a checkBox
		JCheckBox agreeFieldBox = new JCheckBox("Agree");
		root.add(agreeFieldBox);
		agreeFieldBox.setSelected(false);
		
		
		nextButton.setEnabled(false);
		root.add(nextButton);
		
		//Add an action for checkBox
		agreeFieldBox.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				if (agreeFieldBox.isSelected())
					nextButton.setEnabled(true);
				else {
					nextButton.setEnabled(false);
				}
			}
		});
		
		
		colorField.addItem("Red");
		colorField.addItem("Green");
		colorField.addItem("Blue");
		root.add(colorField);
		
		//Add an Test Button
		JButton testButton = new JButton("Test Color");
		root.add(testButton);
		testButton.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				testColor();
			}
		});
		
		
		label2.setText("This is a Label");
		label2.setFont(new Font("Serif", Font.BOLD, 24));
		label2.setForeground(new Color(255,0,0));
		label2.setOpaque(true);
		label2.setBackground(new Color(0,0,255));
		label2.setPreferredSize(new Dimension(260,30));
		label2.setHorizontalAlignment(SwingConstants.CENTER);
		root.add(label2);
	}
	
	public void testColor() {
		int index = colorField.getSelectedIndex();
		System.out.println("Index: " + index);
		int count = colorField.getItemCount();
		String value= colorField.getItemAt(index);
		System.out.println("Index: " + index + ", Value: " + value);
	}
	public void getText() {
		// TODO Auto-generated method stub
		String str = textField.getText();
		System.out.println(str);
	}

	public void showTime() {
		System.out.println("The Button been clicked!");

		// Show the current System time
		SimpleDateFormat sdf = new SimpleDateFormat("HH:mm:ss");
		String timeStr = sdf.format(new Date());
		System.out.println(timeStr);

		timeLabel.setText(timeStr);
	}

}

```

### File: src\my\MyFrame02.java
```java
package my;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.SimpleDateFormat;
import java.util.Date;

import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.SwingConstants;

public class MyFrame02 extends JFrame {

	public MyFrame02(String title) {
		super(title);
		// create a container
		JPanel root = new JPanel();
		this.setContentPane(root);
		
		System.out.println(root.getLayout().getClass().getName());

		JLabel a1 = new ColorLabel("1", Color.YELLOW);
		
		JLabel a2 = new ColorLabel("2", Color.GREEN);
		JLabel a3 = new ColorLabel("3", Color.LIGHT_GRAY);
		JLabel a4 = new ColorLabel("4", Color.CYAN);
		
		
		root.add(a1);
		root.add(a2);
		root.add(a3);
		root.add(a4);
			
	}
	
	private static class ColorLabel extends JLabel {
		public ColorLabel(String text, Color bgColor) {
			
			this.setText(text);
			this.setOpaque(true);
			this.setBackground(bgColor);
			this.setPreferredSize(new Dimension(60,30));
			this.setHorizontalAlignment(SwingConstants.CENTER);
		}
	}

}

```

