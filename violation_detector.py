import cv2
import numpy as np
from datetime import datetime

class ViolationDetector:
    def __init__(self):
        # Speed limits in km/h
        self.speed_limits = {
            'car': 60,
            'truck': 50,
            'bus': 50,
            'motorcycle': 80,
            'bicycle': 25,
            'ambulance': 80,  # Emergency vehicles can exceed limits
            'fire_truck': 80,
            'police': 80
        }

        # Traffic light violation zones (would be configured per intersection)
        self.traffic_light_zones = []

        # Lane violation parameters
        self.lane_tolerance = 0.1  # 10% tolerance for lane position

    def detect_speeding(self, vehicle_type, speed_kmh):
        """Detect if vehicle is speeding"""
        if vehicle_type not in self.speed_limits:
            return False, 60  # Default limit

        limit = self.speed_limits[vehicle_type]
        is_violation = speed_kmh > limit
        return is_violation, limit

    def detect_wrong_lane(self, vehicle_bbox, lane_lines, vehicle_type):
        """Detect if vehicle is in wrong lane"""
        # Simplified lane violation detection
        # In a real system, this would use lane detection models
        if not lane_lines:
            return False

        # Check if vehicle center is within lane boundaries
        vehicle_center_x = (vehicle_bbox[0] + vehicle_bbox[2]) / 2

        # Find which lane the vehicle is in
        for i, lane in enumerate(lane_lines):
            if lane['left'] <= vehicle_center_x <= lane['right']:
                # Check if vehicle type is allowed in this lane
                if vehicle_type in ['truck', 'bus'] and lane.get('truck_lane', True) == False:
                    return True  # Violation - truck in non-truck lane
                break

        return False

    def detect_traffic_light_violation(self, vehicle_bbox, traffic_light_state, vehicle_type):
        """Detect red light violations"""
        if traffic_light_state != 'red':
            return False

        # Check if vehicle crossed the stop line during red light
        # This would require intersection geometry and vehicle tracking
        # For now, simplified logic
        if vehicle_type not in ['ambulance', 'fire_truck', 'police']:  # Emergency vehicles exempt
            # Check if vehicle is in intersection zone during red light
            return self._is_in_intersection_zone(vehicle_bbox)

        return False

    def detect_parking_violation(self, vehicle_bbox, parking_zones):
        """Detect illegal parking"""
        for zone in parking_zones:
            if self._bbox_overlap(vehicle_bbox, zone['bbox']):
                if not zone.get('parking_allowed', True):
                    return True, zone.get('reason', 'No Parking Zone')
        return False, None

    def detect_emergency_vehicle_precedence(self, detections):
        """Check if regular vehicles are blocking emergency vehicles"""
        emergency_vehicles = []
        regular_vehicles = []

        for detection in detections:
            if detection['class'] in ['ambulance', 'fire_truck', 'police']:
                emergency_vehicles.append(detection)
            else:
                regular_vehicles.append(detection)

        violations = []
        for emergency in emergency_vehicles:
            for regular in regular_vehicles:
                if self._vehicles_blocking(emergency['bbox'], regular['bbox']):
                    violations.append({
                        'type': 'blocking_emergency',
                        'emergency_vehicle': emergency['class'],
                        'blocking_vehicle': regular['class']
                    })

        return violations

    def _is_in_intersection_zone(self, vehicle_bbox):
        """Check if vehicle is in intersection during red light"""
        # Simplified - would need actual intersection geometry
        return False

    def _bbox_overlap(self, bbox1, bbox2):
        """Check if two bounding boxes overlap"""
        return not (bbox1[2] < bbox2[0] or bbox1[0] > bbox2[2] or
                   bbox1[3] < bbox2[1] or bbox1[1] > bbox2[3])

    def _vehicles_blocking(self, emergency_bbox, regular_bbox):
        """Check if regular vehicle is blocking emergency vehicle path"""
        # Simplified distance check
        emergency_center = [(emergency_bbox[0] + emergency_bbox[2])/2,
                           (emergency_bbox[1] + emergency_bbox[3])/2]
        regular_center = [(regular_bbox[0] + regular_bbox[2])/2,
                         (regular_bbox[1] + regular_bbox[3])/2]

        distance = np.sqrt((emergency_center[0] - regular_center[0])**2 +
                          (emergency_center[1] - regular_center[1])**2)

        return distance < 100  # Within 100 pixels - arbitrary threshold