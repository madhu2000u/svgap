module grant_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic request,
    output logic grant
);
    logic req_accepted;
    logic grant_pending;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            req_accepted <= 0;
            grant_pending <= 0;
            grant <= 0;
        end else begin
            if (request && !req_accepted) begin
                req_accepted <= 1;
                grant_pending <= 1;
            end

            if (grant_pending) begin
                grant <= 1;
                grant_pending <= 0;
            end else begin
                grant <= 0;
            end
        end
    end
endmodule
