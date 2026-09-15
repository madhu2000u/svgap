module command_deadline(
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    output logic done
);

    logic       pending;
    logic [1:0] count;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            pending <= 1'b0;
            count   <= 2'd0;
            done    <= 1'b0;
        end else begin
            done <= 1'b0;

            if (!pending) begin
                if (start) begin
                    pending <= 1'b1;
                    count   <= 2'd0;
                end
            end else if (count == 2'd2) begin
                pending <= 1'b0;
                count   <= 2'd0;
                done    <= 1'b1;
            end else begin
                count <= count + 2'd1;
            end
        end
    end

endmodule
