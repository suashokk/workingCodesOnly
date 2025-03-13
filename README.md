
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@RestController
@RequestMapping("/collect")
public class FileController {

    private static final String SAVE_DIRECTORY = "/tmp/"; // Change as needed

    @PostMapping(value = "/move", consumes = "application/octet-stream")
    public ResponseEntity<String> moveFile(@RequestBody byte[] fileData,
                                           @RequestParam String fileName) {
        try {
            // Ensure directory exists
            Path savePath = Paths.get(SAVE_DIRECTORY);
            if (!Files.exists(savePath)) {
                Files.createDirectories(savePath);
            }

            // Create the file path with the original filename
            Path filePath = Paths.get(SAVE_DIRECTORY, fileName);

            // Write the file bytes to the destination
            Files.write(filePath, fileData);

            return ResponseEntity.ok("File received and saved at: " + filePath.toString());

        } catch (IOException e) {
            return ResponseEntity.status(500).body("File processing failed: " + e.getMessage());
        }
    }
}



This code is for over netwrok transfer

@PostMapping("/send")
    public ResponseEntity<String> sendFile(@RequestParam("file") MultipartFile file) {
        File tempFile = null;
        try {
            tempFile = convertMultipartFileToFile(file);
            boolean isSent = sendFileToAnotherNetwork(tempFile);
            tempFile.delete();
            return isSent ? ResponseEntity.ok("File sent successfully!") :
                    ResponseEntity.status(HttpStatus.BAD_GATEWAY).body("File sending failed!");
        } catch (IOException e) {
            System.out.println("File processing error: ");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("File processing error!");
        }
    }

    private boolean sendFileToAnotherNetwork(File file) {
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            HttpPost postRequest = new HttpPost(TARGET_SERVICE_URL);
            MultipartEntityBuilder builder = MultipartEntityBuilder.create();
            builder.addBinaryBody("file", file);
            postRequest.setEntity(builder.build());

            try (CloseableHttpResponse response = httpClient.execute(postRequest)) {
                return response.getCode() == 200;
            }
        } catch (Exception e) {
            System.out.println("Error sending file: ");
            return false;
        }
    }
