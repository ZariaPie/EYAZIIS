import java.util.Locale;
import java.util.Scanner;

import javax.speech.AudioException;
import javax.speech.Central;
import javax.speech.EngineException;
import javax.speech.synthesis.Synthesizer;
import javax.speech.synthesis.SynthesizerModeDesc;

public class Main {

    public static void main(String[] args) throws EngineException, AudioException, InterruptedException {
        Scanner scanner = new Scanner(System.in);
        scanner.useDelimiter("\n");
        System.setProperty(
            "freetts.voices",
            "com.sun.speech.freetts.en.us" + ".cmu_us_kal.KevinVoiceDirectory");
        Central.registerEngineCentral(
            "com.sun.speech.freetts"
                + ".jsapi.FreeTTSEngineCentral");
        Synthesizer synthesizer = Central.createSynthesizer(new SynthesizerModeDesc(Locale.US));
        synthesizer.allocate();

        while (true) {
            System.out.println("write");
            String str = scanner.nextLine();
            synthesizer.resume();
            synthesizer.speakPlainText(str, null);
            synthesizer.waitEngineState(Synthesizer.QUEUE_EMPTY);
        }

    }

}
