// File: Sample.java

public class Sample {
    
    private void setWay(int[][] map) {
        // Bad method name, unclear logic
        for (int i = 0; i < map.length; i++) {
            for (int j = 0; j < map[0].length; j++) {
                map[i][j] = 1;
            }
        }
    }

    private int unusedHelper(int x) {
        return x * 42;
    }

    public static void main(String[] args) {
        System.out.println("Running...");
    }
}
