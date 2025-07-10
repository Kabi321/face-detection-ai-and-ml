import numpy as np

class CentroidTracker:
    def __init__(self, maxDisappeared=50, maxDistance=50):
        self.nextObjectID = 0
        self.objects = {}           # objectID -> (x, y, w, h)
        self.centroids = {}         # objectID -> (cx, cy)
        self.disappeared = {}       # objectID -> frame count
        self.maxDisappeared = maxDisappeared
        self.maxDistance = maxDistance

    def register(self, rect):
        x, y, w, h = rect
        cx = x + w // 2
        cy = y + h // 2
        self.objects[self.nextObjectID] = rect
        self.centroids[self.nextObjectID] = (cx, cy)
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):
        del self.objects[objectID]
        del self.centroids[objectID]
        del self.disappeared[objectID]

    def update(self, rects):
        if len(rects) == 0:
            # Increment disappeared count
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
            return self.objects

        inputCentroids = []
        for (x, y, w, h) in rects:
            cX = x + w // 2
            cY = y + h // 2
            inputCentroids.append((cX, cY))

        if len(self.objects) == 0:
            for rect in rects:
                self.register(rect)
        else:
            objectIDs = list(self.centroids.keys())
            objectCentroids = list(self.centroids.values())

            D = np.linalg.norm(np.array(objectCentroids)[:, np.newaxis] - np.array(inputCentroids), axis=2)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue

                if D[row, col] > self.maxDistance:
                    continue

                objectID = objectIDs[row]
                self.centroids[objectID] = inputCentroids[col]
                self.objects[objectID] = rects[col]
                self.disappeared[objectID] = 0

                usedRows.add(row)
                usedCols.add(col)

            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, len(inputCentroids))).difference(usedCols)

            for row in unusedRows:
                objectID = objectIDs[row]
                self.disappeared[objectID] += 1
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            for col in unusedCols:
                self.register(rects[col])

        return self.objects
