import java.io.*;
import java.net.*;
import java.util.*;
//Timestamp and date used for formatting on server's end
import java.sql.Timestamp;
import java.util.Date;

/*
 * Client to send ping requests over UDP.
 */
public class rPingClient
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
      int sequenceNumber = 0;
      int numLost = 0;
      long beginTime = System.nanoTime();
      //while loop used to increment sequenceNumber only when packet delivered successfuly
      while(sequenceNumber < 5){
         try{
            byte[] buf = new byte[1024];

            //Delay so pings are about 1 second apart, excluding RTT/losses.  Excluded for rPingClient.java
            //Thread.sleep(1000);

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

            //only move on to next packet if no timeout occurs
            sequenceNumber++;
            //since packet successfuly delivered, reset counter for next packet
            numLost = 0;
         }
         //In case of lost packets
         catch(SocketTimeoutException e){
            System.out.println("PING "+ serverAddress+ " "+ sequenceNumber+ " LOST");
            numLost++;
            if(numLost >= 10){
               System.out.println("Error: unable to establish reliable connection with server");
               System.exit(1);
            }
         }
      }
      double deliveryTime = (System.nanoTime()-beginTime)/1000/1000.0;
      System.out.println("All packets successfuly delivered.  Delivery time: " + deliveryTime);
   }
}