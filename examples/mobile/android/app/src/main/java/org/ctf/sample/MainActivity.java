package org.ctf.sample;
public class MainActivity extends android.app.Activity {
 @Override public void onCreate(android.os.Bundle state) { super.onCreate(state); android.widget.TextView view = new android.widget.TextView(this); view.setText("Analiza los recursos de esta aplicación"); setContentView(view); }
}
