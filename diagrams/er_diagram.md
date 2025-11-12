erDiagram

    Tenant ||--o{ User : Tenant has many users
    Tenant ||--o{ Assessment : Tenant owns many assessments
    Tenant ||--o{ Lead : Tenant has many leads
    Tenant ||--o{ QRCode : Tenant creates many QR codes
    Tenant ||--o{ Integration : Tenant configures many integrations
    Assessment ||--o{ Question : Assessment contains many questions
    Assessment ||--o{ Response : Assessment receives many responses
    Assessment ||--o{ QRCode : Assessment can have multiple QR codes
    Question ||--o{ QuestionOption : Question has multiple choice options
    Question ||--o{ Answer : Question receives many answers
    Response ||--o{ Answer : Response contains many answers
    Response ||--o{ Lead : Response may generate leads
    QRCode ||--o{ QRCodeScan : QRCode has many scans