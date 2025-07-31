import org.junit.jupiter.api.Test;
import org.mockito.MockedConstruction;

import java.io.ByteArrayInputStream;
import java.io.IOException;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class TradeNodeUtilTest {

    @Test
    void testExecuteCurlCommand_mocked() throws Exception {
        String expectedOutputPath = "mock-output.json";
        String fakeAuthorization = "Bearer token";
        String fakeUrl = "http://mockurl";

        // Mock ProcessBuilder & Process
        try (MockedConstruction<ProcessBuilder> mockedPB =
                     mockConstruction(ProcessBuilder.class,
                             (mockBuilder, context) -> {
                                 Process mockProcess = mock(Process.class);
                                 when(mockProcess.getInputStream())
                                         .thenReturn(new ByteArrayInputStream("mock curl output".getBytes()));
                                 when(mockProcess.waitFor()).thenReturn(0);

                                 when(mockBuilder.start()).thenReturn(mockProcess);
                             })) {

            String result = TradeNodeUtil.executeCurlCommand(
                    expectedOutputPath,
                    fakeAuthorization,
                    fakeUrl
            );

            assertEquals(expectedOutputPath, result);
        }
    }

    @Test
    void testExecuteCurlCommand_failure() throws Exception {
        try (MockedConstruction<ProcessBuilder> mockedPB =
                     mockConstruction(ProcessBuilder.class,
                             (mockBuilder, context) -> {
                                 Process mockProcess = mock(Process.class);
                                 when(mockProcess.getInputStream())
                                         .thenReturn(new ByteArrayInputStream("error".getBytes()));
                                 when(mockProcess.waitFor()).thenReturn(1); // Simulate failure
                                 when(mockBuilder.start()).thenReturn(mockProcess);
                             })) {

            assertThrows(RuntimeException.class, () ->
                    TradeNodeUtil.executeCurlCommand("out.json", "auth", "url")
            );
        }
    }
}

Got it — I can prepare a Java 17 JUnit test case for your executeCurlCommand method.
From your screenshot, your method signature is:

public static String executeCurlCommand(
        String outputFolderFileName,
        String authorizationHeader,
        String url)

It internally runs a curl command via ProcessBuilder.


---

Key points for a JUnit 5 working test in Java 17

Since your method executes an external command (curl), a pure unit test would require mocking ProcessBuilder to avoid actually running curl in tests.
We can achieve this using:

1. Mockito (to mock ProcessBuilder and Process).


2. JUnit 5 (@Test with Assertions).


3. Temporary folder/files to verify if output is written correctly (if you want to test actual execution).




---

1. Maven dependencies (JUnit 5 + Mockito)

<dependencies>
    <!-- JUnit 5 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.0</version>
        <scope>test</scope>
    </dependency>

    <!-- Mockito -->
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <version>5.5.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>


---

2. Example unit test without actually calling curl

import org.junit.jupiter.api.Test;
import org.mockito.MockedConstruction;

import java.io.ByteArrayInputStream;
import java.io.IOException;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class TradeNodeUtilTest {

    @Test
    void testExecuteCurlCommand_mocked() throws Exception {
        String expectedOutputPath = "mock-output.json";
        String fakeAuthorization = "Bearer token";
        String fakeUrl = "http://mockurl";

        // Mock ProcessBuilder & Process
        try (MockedConstruction<ProcessBuilder> mockedPB =
                     mockConstruction(ProcessBuilder.class,
                             (mockBuilder, context) -> {
                                 Process mockProcess = mock(Process.class);
                                 when(mockProcess.getInputStream())
                                         .thenReturn(new ByteArrayInputStream("mock curl output".getBytes()));
                                 when(mockProcess.waitFor()).thenReturn(0);

                                 when(mockBuilder.start()).thenReturn(mockProcess);
                             })) {

            String result = TradeNodeUtil.executeCurlCommand(
                    expectedOutputPath,
                    fakeAuthorization,
                    fakeUrl
            );

            assertEquals(expectedOutputPath, result);
        }
    }

    @Test
    void testExecuteCurlCommand_failure() throws Exception {
        try (MockedConstruction<ProcessBuilder> mockedPB =
                     mockConstruction(ProcessBuilder.class,
                             (mockBuilder, context) -> {
                                 Process mockProcess = mock(Process.class);
                                 when(mockProcess.getInputStream())
                                         .thenReturn(new ByteArrayInputStream("error".getBytes()));
                                 when(mockProcess.waitFor()).thenReturn(1); // Simulate failure
                                 when(mockBuilder.start()).thenReturn(mockProcess);
                             })) {

            assertThrows(RuntimeException.class, () ->
                    TradeNodeUtil.executeCurlCommand("out.json", "auth", "url")
            );
        }
    }
}


---

3. If you want an integration test (actually runs curl)

import org.junit.jupiter.api.Test;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

public class TradeNodeUtilIntegrationTest {

    @Test
    void testExecuteCurlCommand_realCurl() throws Exception {
        Path tempFile = Files.createTempFile("curl-test", ".txt");

        String output = TradeNodeUtil.executeCurlCommand(
                tempFile.toString(),
                "Bearer dummy", // If endpoint requires real token, change this
                "https://postman-echo.com/get"
        );

        assertTrue(Files.exists(tempFile));
        assertEquals(tempFile.toString(), output);
    }
}

> ⚠ Integration test needs curl installed and internet access.
For CI/CD or offline testing, stick to the mocked version.




---

If you want, I can now give you a ready-to-run Java 17 JUnit test class zip for your current method so you can just run it and see green ✅ in IntelliJ without modifying your main code.

Do you want me to prepare that ready-to-run JUnit test zip?

import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.StringReader;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;

public class TradeNodeUtilTest {

    @Test
    void testParseObjectFactoryXml_callsExecuteCurlCommand() throws Exception {
        // Create a mock for TradeNodeUtil (static methods require mockStatic in Mockito)
        try (var mocked = Mockito.mockStatic(TradeNodeUtil.class, Mockito.CALLS_REAL_METHODS)) {

            // Mock executeCurlCommand to just return dummy path
            mocked.when(() -> TradeNodeUtil.executeCurlCommand(any(), any(), any()))
                    .thenReturn("mock-output.json");

            // Prepare test XML string
            String xmlContent = """
                    <object-factory>
                        <directory name="dir1">
                            <entry name="file1"/>
                            <entry name="file2"/>
                        </directory>
                    </object-factory>
                    """;

            // Parse XML string into Document
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(new InputSource(new StringReader(xmlContent)));

            // Call method under test
            TradeNodeUtil.parseObjectFactoryXml("mock-output-folder", "Bearer token", "http://mockurl");

            // Verify executeCurlCommand was called (expected times may vary)
            mocked.verify(() -> TradeNodeUtil.executeCurlCommand(any(), any(), any()), atLeastOnce());
        }
    }
}


import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.w3c.dom.Document;
import org.xml.sax.InputSource;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.StringReader;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

public class TradeNodeUtilTest {

    @Test
    void testParseObjectFactoryXml_MockedCurl() throws Exception {
        // Mock static method executeCurlCommand
        try (var mocked = Mockito.mockStatic(TradeNodeUtil.class, Mockito.CALLS_REAL_METHODS)) {

            // Mock curl to just return dummy output path
            mocked.when(() -> TradeNodeUtil.executeCurlCommand(any(), any(), any()))
                    .thenReturn("mock-output.json");

            // Sample XML with a directory and two entries
            String xml = """
                    <object-factory>
                        <directory name="dir1">
                            <entry name="file1"/>
                            <entry name="file2"/>
                        </directory>
                    </object-factory>
                    """;

            // Parse XML string to Document
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(new InputSource(new StringReader(xml)));

            // Directly call parseObjectFactory with mock Document root
            TradeNodeUtil.parseObjectFactory(doc.getDocumentElement(),
                    "mock-output-folder", "Bearer token", "http://mockurl");

            // Verify curl was called twice (once for each entry)
            mocked.verify(() -> TradeNodeUtil.executeCurlCommand(
                    any(), any(), any()), times(2));
        }
    }
}

import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.io.ByteArrayInputStream;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

public class TradeNodeUtilTest {

    @Test
    void testExecuteCurlCommand_mockedProcess() throws Exception {
        // Mock ProcessBuilder and Process for this test
        try (var mockedPB = Mockito.mockConstruction(ProcessBuilder.class,
                (mockBuilder, context) -> {
                    // Mock process that returns fake output and exit code 0
                    Process mockProcess = mock(Process.class);
                    when(mockProcess.getInputStream())
                            .thenReturn(new ByteArrayInputStream("mock curl output".getBytes()));
                    when(mockProcess.waitFor()).thenReturn(0);
                    when(mockBuilder.start()).thenReturn(mockProcess);
                })) {

            String result = TradeNodeUtil.executeCurlCommand(
                    "dummy-output-file.json",
                    "Bearer token",
                    "http://mockurl"
            );

            // Ensure the method returns the expected output path
            org.junit.jupiter.api.Assertions.assertEquals("dummy-output-file.json", result);
        }
    }

    @Test
    void testExecuteCurlCommand_failureExitCode() throws Exception {
        // Mock ProcessBuilder to simulate failure
        try (var mockedPB = Mockito.mockConstruction(ProcessBuilder.class,
                (mockBuilder, context) -> {
                    Process mockProcess = mock(Process.class);
                    when(mockProcess.getInputStream())
                            .thenReturn(new ByteArrayInputStream("error".getBytes()));
                    when(mockProcess.waitFor()).thenReturn(1); // non-zero exit code
                    when(mockBuilder.start()).thenReturn(mockProcess);
                })) {

            org.junit.jupiter.api.Assertions.assertThrows(RuntimeException.class, () ->
                    TradeNodeUtil.executeCurlCommand(
                            "dummy-output-file.json",
                            "Bearer token",
                            "http://mockurl"
                    )
            );
        }
    }
}
