 #include <iostream>                                                                                                                                                                                      
 #include <chrono>                                                                                                                                                                                        
 #include <thread>                                                                                                                                                                                        
                                                                                                                                                                                                          
 using namespace std;                                                                                                                                                                                     
                                                                                                                                                                                                          
 enum class TrafficSignalState {                                                                                                                                                                          
     Green,                                                                                                                                                                                               
     Yellow,                                                                                                                                                                                              
     Red                                                                                                                                                                                                  
 };                                                                                                                                                                                                       
                                                                                                                                                                                                          
 enum class PedestrianSignalState {                                                                                                                                                                       
     Walk,                                                                                                                                                                                                
     DontWalk                                                                                                                                                                                             
 };                                                                                                                                                                                                       
                                                                                                                                                                                                          
 class TrafficSignalControlSystem {                                                                                                                                                                       
 public:                                                                                                                                                                                                  
     TrafficSignalControlSystem() :                                                                                                                                                                       
         currentState(TrafficSignalState::Green),                                                                                                                                                         
         pedestrianSignalState(PedestrianSignalState::DontWalk) {}                                                                                                                                        
                                                                                                                                                                                                          
     // Transition functions                                                                                                                                                                              
     void transitionToIdle();                                                                                                                                                                             
     void transitionToPedestrianCrossing();                                                                                                                                                               
     void transitionToTrafficIntersection();                                                                                                                                                              
                                                                                                                                                                                                          
     // Action functions                                                                                                                                                                                  
     void performIdleActions();                                                                                                                                                                           
     void performPedestrianCrossingActions();                                                                                                                                                             
     void performGreenActions();                                                                                                                                                                          
     void performYellowActions();                                                                                                                                                                         
     void performRedActions();                                                                                                                                                                            
                                                                                                                                                                                                          
     // Start the traffic signal system                                                                                                                                                                   
     void start();                                                                                                                                                                                        
                                                                                                                                                                                                          
 private:                                                                                                                                                                                                 
     TrafficSignalState currentState;                                                                                                                                                                     
     PedestrianSignalState pedestrianSignalState;                                                                                                                                                         
                                                                                                                                                                                                          
     // Helpers                                                                                                                                                                                           
     void changeLight(TrafficSignalState nextState);                                                                                                                                                      
     void changePedestrianSignal(PedestrianSignalState nextState);                                                                                                                                        
 };                                                                                                                                                                                                       
                                                                                                                                                                                                          
 void TrafficSignalControlSystem::transitionToIdle() {                                                                                                                                                    
     currentState = TrafficSignalState::Green;                                                                                                                                                            
     pedestrianSignalState = PedestrianSignalState::DontWalk;                                                                                                                                             
 }                                                                                                                                                                                                        
                                                                                                                                                                                                          
 void TrafficSignalControlSystem::transitionToPedestrianCrossing() {                                                                                                                                      
     currentState = TrafficSignalState::Red;                                                                                                                                                              
     pedestrianSignalState = PedestrianSignalState::Walk;                                                                                                                                                 
 }                                                                                                                                                                                                        
                                                                                                                                                                                                          
 void TrafficSignalControlSystem::transitionToTrafficIntersection() {                                                                                                                                     
     currentState = TrafficSignalState::Green;                                                                                                                                                            
     pedestrianSignalState = PedestrianSignalState::DontWalk;                                                                                                                                             
 }                                                                                                                                                                                                        
                                                                                                                                                                                                          
 void TrafficSignalControlSystem::performIdleActions() {                                                                                                                                                  
     cout << "Traffic signal is in idle. No traffic or pedestrians." << endl;                                                                                                                             
 }                                                                                                                                                                                                        
                                                                                                                                                                                                          
 void TrafficSignalControlSystem::performPedestrianCrossingActions() {                                                                                                                                    
     cout << "Traffic signal is in pedestrian crossing mode. Cars stopped, pedestrians can walk." << endl;                                                                                                
 }                                                                                                                                                                                                        
                                                                                                                                                                                                          
 void TrafficSignalControlSystem::performGreenActions() {                                                                                                                                                 
     cout << "Traffic light is green. Cars can proceed." << endl;                                                                                                                                         
 }                                                                                                                                                                                                        
                                                                                                                                                                                                          
 void TrafficSignalControlSystem::performYellowActions() {                                                                                                                                                
     cout << "Traffic light is yellow. Cars should prepare to stop." << endl;                                                                                                                             
 }                                                                                                                                                                                                        
                                                                                                                                                                                                          
 void TrafficSignalControlSystem::performRedActions() {                                                                                                                                                   
     cout << "Traffic light is red. Cars should stop." << endl;                                                                                                                                           
 }                                                                                                                                                                                                        
                                                                                                                                                                                                          
void TrafficSignalControlSystem::changeLight(TrafficSignalState nextState)
 {                                                                                            
     switch (nextState) {                                                                     
         case TrafficSignalState::Green:                                                      
             performGreenActions();                                                           
             break;                                                                           
         case TrafficSignalState::Yellow:                                                     
             performYellowActions();                                                          
             break;                                                                           
         case TrafficSignalState::Red:                                                        
             performRedActions();                                                             
             break;                                                                           
     }                                                                                        
     return;
 }                                                                                            
                                                                                              
 void TrafficSignalControlSystem::changePedestrianSignal(PedestrianSignalState nextState) {   
     switch (nextState) {                                                                     
         case PedestrianSignalState::Walk:                                                    
             cout << "Pedestrian can now walk." << endl;                                      
             break;                                                                           
         case PedestrianSignalState::DontWalk:                                                
             cout << "Pedestrian should not walk. Wait for the signal." << endl;              
             break;                                                                           
     }                                                                                        
 }                                                                                            

 void TrafficSignalControlSystem::start() {                                                                                                                                                               
     // Traffic signal loop                                                                                                                                                                               
     bool isTransitionAllowed = true;                                                                                                                                                                     
                                                                                                                                                                                                          
     while (true) {                                                                                                                                                                                       
         switch (currentState) {                                                                                                                                                                          
             case TrafficSignalState::Green:                                                                                                                                                              
                 if (isTransitionAllowed) {                                                                                                                                                               
                    // changeLight(TrafficSignalState::Yellow);
                    this_thread::sleep_for(chrono::seconds(3)); // Simulating yellow time                                                                                                                
                 }                                                                                                                                                                                        
                 isTransitionAllowed = true;                                                                                                                                                              
                 break;                                                                                                                                                                                   
             case TrafficSignalState::Yellow:                                                                                                                                                             
                 if (isTransitionAllowed) {                                                                                                                                                               
                     changeLight(TrafficSignalState::Red);                                                                                                                                                
                     changePedestrianSignal(PedestrianSignalState::Walk);                                                                                                                                 
                     this_thread::sleep_for(chrono::seconds(5)); // Simulating red time                                                                                                                   
                 }                                                                                                                                                                                        
                 isTransitionAllowed = true;                                                                                                                                                              
                 break;                                                                                                                                                                                   
             case TrafficSignalState::Red:                                                                                                                                                                
                 if (isTransitionAllowed) {                                                                                                                                                               
                     changeLight(TrafficSignalState::Green);                                                                                                                                              
                     changePedestrianSignal(PedestrianSignalState::DontWalk);                                                                                                                             
                     this_thread::sleep_for(chrono::seconds(10)); // Simulating green time                                                                                                                
                 }                                                                                                                                                                                        
                 isTransitionAllowed = true;                                                                                                                                                              
                 break;                                                                                                                                                                                   
         }                                                                                                                                                                                                
                                                                                                                                                                                                          
         // Set transition flag to false to prevent immediate transition to a new state                                                                                                                   
         isTransitionAllowed = false;                                                                                                                                                                     
     }                                                                                                                                                                                                    
 }                                                                                                                                                                                                        

                                                                                              
 int main() {                                                                                 
     TrafficSignalControlSystem system;                                                       
     cout<<"hello";
     system.start();                                                                          
                                                                                              
     return 0;                                                                                
 }
