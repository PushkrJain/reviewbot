// File: Sample.java

//  Recommendation (Severity 7): Method name 'setWay' is unclear and doesn't reflect the functionality.
//  Rename method to 'initializeMap'.
public class Sample {
    
    private void setWay(int[][] map) {
        // Bad method name, unclear logic
        for (int i = 0; i < map.length; i++) {
            for (int j = 0; j < map[0].length; j++) {
                map[i][j] = 1;
            }
        }
    }
//  Recommendation (Severity 2): Unused method 'unusedHelper(int)'.
//  Remove unused code or refactor for reuse.

    private int unusedHelper(int x) {
        return x * 42;
    }

    public static void main(String[] args) {
        System.out.println("Running...");
    }
}