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
