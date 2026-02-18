import java.io.*;
import java.net.*;
import java.util.*;
//Timestamp and date used for formatting on server's end
import java.sql.Timestamp;
import java.util.Date;

/*
 * Client to send ping requests over UDP.
 */
public class PingClient
{
   public static void main(String[] args) throws Exception
   {
      // Get command line argument.
      if (args.length != 2) {
         System.out.println("Required arguments: hostname, port");
         return;
      }
      String serverName = args[0];
      int serverPort = Integer.parseInt(args[1]);
      InetAddress serverAddress = InetAddress.getByName(serverName);
      
      // Create a datagram socket for receiving and sending UDP packets
      // through the port specified on the command line.
      DatagramSocket clientSocket = new DatagramSocket();
      clientSocket.setSoTimeout(1000);

      // Processing loop.
      for(int sequenceNumber = 0; sequenceNumber < 5; sequenceNumber++){
         try{
            byte[] buf = new byte[1024];

            //Delay so pings are about 1 second apart, excluding RTT/losses
            Thread.sleep(1000);
            
            Timestamp startTS = new Timestamp(System.currentTimeMillis());

            long startNanos = System.nanoTime();
            String message = "PING number " + sequenceNumber + " timestamp: " + startTS.toString() + "ms";
            buf = message.getBytes();
            DatagramPacket clientPacket = new DatagramPacket(buf, buf.length, serverAddress, serverPort);
            clientSocket.send(clientPacket);
            
            // Create a datagram packet to hold incomming UDP packet.
            DatagramPacket serverPacket = new DatagramPacket(new byte[1024], 1024);

            // Block until the client receives a UDP packet.
            clientSocket.receive(serverPacket);
         
            //Compare current time with start time and round to receive RTT with microsecond precision
            double rtt = (System.nanoTime()-startNanos)/1000/1000.0;
            System.out.println("PING "+ serverAddress+ " packet number "+ sequenceNumber + " estimated RTT: "+  rtt + "ms");
            
         }
         //In case of lost packets
         catch(SocketTimeoutException e){
            System.out.println("PING "+ serverAddress+ " "+ sequenceNumber+ " LOST");
         }
      }
   }
}