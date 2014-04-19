import java.io.*;
import java.net.*;

public class Parse {

    public static void main(String[][] args) {
        String fromClient;
        String toClient;

        try {
            ServerSocket server = new ServerSocket(5002);

            while(true) {
                Socket connected = server.accept();
                System.out.println("The client is connected.");

                BufferedReader clientReader = new BufferedReader(
                        new InputStreamReader(connected.getInputStream()));

                PrintWriter clientWriter = new PrintWriter(
                        connected.getOutputStream(), true);

                while(true) {
                    StringBuilder builder = new StringBuilder();
                    
                    while((fromClient = clientReader.readLine()) != null) {
                        builder.append(fromClient);
                    }

                    fromClient = builder.toString();

                    //Handle the data from the client here
                }
            }
        } catch (IOException ex) {
        
        }
    }

}
