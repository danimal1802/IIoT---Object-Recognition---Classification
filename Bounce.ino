

// Daniel Mitchell
// IIoT Fall 2020 - Semester Project
// 23 Nov 2020
// This Arduino controls the 2HSS60 motor Contoller and servo fucntions

#include <AccelStepper.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd = LiquidCrystal_I2C(0x27, 20, 4); // Change to (0x27,20,4) for 20x4 LCD.

// Define a stepper and the pins it will use
// AccelStepper stepper; 
AccelStepper stepper(1,7,6); 
// pulse and dir

void setup()
{  
  // Initiate the LCD screen:
  lcd.init();
  lcd.backlight();
  // Change these to suit your stepper if you want
  stepper.setMaxSpeed(1000);
  stepper.setAcceleration(10000);
  //stepper.moveTo(2000);

  pinMode(8, INPUT); // This pin is to sense the direction switch

   // Initialize display
   lcd.setCursor(0,0); 
   lcd.print("Daniel Mitchell");
   lcd.setCursor(0,1); 
   lcd.print("IIoT Fall 2020"); 
   //lcd.print("Linear Track controller ");
}

void loop()
{

    // If at the end of travel go to the other end
    //if (stepper.distanceToGo() == 0)
    //stepper.moveTo(-stepper.currentPosition());
    //stepper.run();

    // 
    if (digitalRead(8)) {
        stepper.moveTo(4500);
        stepper.run();
    }
    else {
        stepper.moveTo(0);
        stepper.run();
    }
}
