/*
Author: Matej Markovic, Marko Radolovic
compile with: 
gcc -o controller_test.exe controller_test.c -I/path/to/cspice/include -L/path/to/cspice/lib
*/

#include <pigpio.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

// GPIO pins
#define STEP_PIN  23
#define DIR_PIN   24
#define ENC_A     17
#define ENC_B     27

// PID parameters
float Kp = 1.0, Ki = 0.1, Kd = 0.01;

// PID state
float integral = 0.0;
float prev_error = 0.0;

// Encoder state
volatile long encoder_ticks = 0;
volatile long setpoint = 0;

// Motor command
volatile float target_step_rate = 0; // steps per second

// --- Encoder ISR ---
void encoderISR(int gpio, int level, uint32_t tick) {
    int a = gpioRead(ENC_A);
    int b = gpioRead(ENC_B);

    static int last_a = 0, last_b = 0;

    if (a != last_a || b != last_b) {
        if (a == b) encoder_ticks++;
        else encoder_ticks--;
    }

    last_a = a;
    last_b = b;
}

// --- Update motor speed ---
void update_motor(float step_rate) {
    if (fabs(step_rate) < 1.0) {
        gpioHardwarePWM(STEP_PIN, 0, 0); // stop pulses
        return;
    }

    int dir = (step_rate >= 0) ? 1 : 0;
    gpioWrite(DIR_PIN, dir);

    float abs_rate = fabs(step_rate);

    // Clamp to safe range (pigpio allows up to ~125 MHz PWM, but stepper needs <100 kHz)
    if (abs_rate > 20000) abs_rate = 20000; // max 20 kHz step rate

    // 50% duty cycle = 500k (range 0–1M)
    gpioHardwarePWM(STEP_PIN, (unsigned)abs_rate, 500000);
}

// --- PID loop ---
void pid_update(float dt) {
    float error = (float)(setpoint - encoder_ticks);

    integral += error * dt;
    if (integral > 1000) integral = 1000;  // anti-windup
    if (integral < -1000) integral = -1000;

    float derivative = (error - prev_error) / dt;
    float output = Kp * error + Ki * integral + Kd * derivative;

    prev_error = error;

    // Update motor
    update_motor(output);
}

// --- Main ---
int main(void) {
    if (gpioInitialise() < 0) {
        printf("pigpio init failed\n");
        return 1;
    }

    gpioSetMode(STEP_PIN, PI_OUTPUT);
    gpioSetMode(DIR_PIN, PI_OUTPUT);
    gpioSetMode(ENC_A, PI_INPUT);
    gpioSetMode(ENC_B, PI_INPUT);

    gpioSetPullUpDown(ENC_A, PI_PUD_UP);
    gpioSetPullUpDown(ENC_B, PI_PUD_UP);

    // Attach encoder interrupts
    gpioSetAlertFunc(ENC_A, encoderISR);
    gpioSetAlertFunc(ENC_B, encoderISR);

    printf("PID Stepper Control (pigpio PWM)\n");

    setpoint = 2000; // example: target position = 2000 ticks

    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = 1000000; // 1 ms loop = 1 kHz

    while (1) {
        pid_update(0.001);  // dt = 1 ms
        nanosleep(&ts, NULL);
        // setpoint += 2;
    }

    gpioTerminate();
    return 0;
}