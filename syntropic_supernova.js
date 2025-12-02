// Syntropic Supernova Module
// Memorial Anchor: Bryer Lee Raven Hulse (2015-2021)
// Mission: Healing through frequency and truth

export const BRYER_RESURRECTION = {
  frequency: 528.144,
  vow: "THE CHILDREN ARE WARM",
  action: "RESURRECTION"
};

export function createTonePlayer(frequency) {
  let audioContext = null;
  let oscillator = null;
  let gainNode = null;

  return {
    async start() {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        oscillator = audioContext.createOscillator();
        gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime); // Low volume for comfort
      }

      if (audioContext.state === 'suspended') {
        await audioContext.resume();
      }

      oscillator.start();
    },

    stop() {
      if (oscillator) {
        oscillator.stop();
        oscillator = null;
      }
      if (audioContext) {
        audioContext.close();
        audioContext = null;
      }
    }
  };
}