const json = {
  key: "AYxYp8z_gAol-fhPXu8s",
  rule: "java:S1192",
  severity: "CRITICAL",
  component:
    "dglalperen_reservation-service:src/main/java/dev/cassandraguide/repository/ReservationRepository.java",
  project: "dglalperen_reservation-service",
  line: 347,
  hash: "e43913115413879c2128fbc4eb1fa1d1",
  textRange: { startLine: 347, endLine: 347, startOffset: 21, endOffset: 64 },
  flows: [
    {
      locations: [
        {
          component:
            "dglalperen_reservation-service:src/main/java/dev/cassandraguide/repository/ReservationRepository.java",
          textRange: {
            startLine: 347,
            endLine: 347,
            startOffset: 21,
            endOffset: 64,
          },
          msg: "Duplication",
        },
      ],
    },
    {
      locations: [
        {
          component:
            "dglalperen_reservation-service:src/main/java/dev/cassandraguide/repository/ReservationRepository.java",
          textRange: {
            startLine: 368,
            endLine: 368,
            startOffset: 22,
            endOffset: 65,
          },
          msg: "Duplication",
        },
      ],
    },
    {
      locations: [
        {
          component:
            "dglalperen_reservation-service:src/main/java/dev/cassandraguide/repository/ReservationRepository.java",
          textRange: {
            startLine: 393,
            endLine: 393,
            startOffset: 23,
            endOffset: 66,
          },
          msg: "Duplication",
        },
      ],
    },
    {
      locations: [
        {
          component:
            "dglalperen_reservation-service:src/main/java/dev/cassandraguide/repository/ReservationRepository.java",
          textRange: {
            startLine: 422,
            endLine: 422,
            startOffset: 24,
            endOffset: 67,
          },
          msg: "Duplication",
        },
      ],
    },
  ],
  status: "OPEN",
  message:
    "Define a constant instead of duplicating this literal \"+ Table '{}' has been created (if needed)\"4 times.",
  effort: "10min",
  debt: "10min",
  author: "jeffreyscarpenter@cox.net",
  tags: ["design"],
  transitions: ["confirm", "resolve", "falsepositive", "wontfix"],
  actions: ["set_type", "set_tags", "comment", "set_severity", "assign"],
  comments: [],
  creationDate: "2019-07-16T02: 10: 58+0200",
  updateDate: "2023-12-11T12: 33: 43+0100",
  type: "CODE_SMELL",
  organization: "dglalperen",
  cleanCodeAttribute: "DISTINCT",
  cleanCodeAttributeCategory: "ADAPTABLE",
  impacts: [{ softwareQuality: "MAINTAINABILITY", severity: "HIGH" }],
};
